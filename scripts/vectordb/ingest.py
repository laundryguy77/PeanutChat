#!/usr/bin/env python3
"""Ingestion pipeline for markdown documentation into ChromaDB."""

import argparse
import sys
from pathlib import Path

import chromadb

from config import COLLECTION_NAME, get_db_path, get_docs_path
from markdown_chunker import MarkdownChunker
from ollama_embed import OllamaConnectionError, OllamaEmbedder, OllamaModelError


def progress_bar(current: int, total: int, width: int = 40) -> str:
    """Generate a simple progress bar string."""
    filled = int(width * current / total)
    bar = '=' * filled + '-' * (width - filled)
    percent = 100 * current / total
    return f"[{bar}] {percent:.1f}% ({current}/{total})"


def ingest_documents(
    docs_dir: Path,
    db_path: Path,
    rebuild: bool = False,
    single_file: str = None
) -> dict:
    """
    Ingest markdown documents into ChromaDB.

    Args:
        docs_dir: Directory containing markdown files
        db_path: Path for ChromaDB storage
        rebuild: If True, delete existing collection first
        single_file: If specified, only process this file

    Returns:
        Dict with stats: files_processed, chunks_created, errors
    """
    stats = {"files_processed": 0, "chunks_created": 0, "errors": []}

    # Initialize embedder
    print("Connecting to Ollama...")
    try:
        embedder = OllamaEmbedder()
        print("  Connected successfully")
    except OllamaConnectionError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except OllamaModelError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Initialize ChromaDB
    print(f"\nInitializing ChromaDB at {db_path}...")
    client = chromadb.PersistentClient(path=str(db_path))

    if rebuild:
        # Delete existing collection
        try:
            client.delete_collection(name=COLLECTION_NAME)
            print("  Deleted existing collection")
        except (ValueError, Exception) as e:
            # Collection doesn't exist - NotFoundError or ValueError depending on version
            if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                pass
            else:
                raise

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    print(f"  Collection '{COLLECTION_NAME}' ready")

    # Find markdown files
    if single_file:
        md_files = [docs_dir / single_file]
        if not md_files[0].exists():
            print(f"ERROR: File not found: {md_files[0]}")
            sys.exit(1)
    else:
        md_files = sorted(docs_dir.glob("*.md"))

    if not md_files:
        print(f"ERROR: No markdown files found in {docs_dir}")
        sys.exit(1)

    print(f"\nFound {len(md_files)} markdown files")

    # Initialize chunker
    chunker = MarkdownChunker()

    # Process each file
    all_chunks = []
    for md_file in md_files:
        print(f"\nProcessing: {md_file.name}")
        try:
            chunks = chunker.chunk_file(md_file)
            print(f"  Created {len(chunks)} chunks")
            all_chunks.extend(chunks)
            stats["files_processed"] += 1
        except Exception as e:
            error_msg = f"Failed to chunk {md_file.name}: {e}"
            print(f"  ERROR: {error_msg}")
            stats["errors"].append(error_msg)

    if not all_chunks:
        print("ERROR: No chunks created from documents")
        sys.exit(1)

    print(f"\nTotal chunks to embed: {len(all_chunks)}")

    # Generate embeddings
    print("\nGenerating embeddings...")
    texts = [chunk.content for chunk in all_chunks]

    def show_progress(current, total):
        sys.stdout.write(f"\r  {progress_bar(current, total)}")
        sys.stdout.flush()

    embeddings = embedder.embed_batch(texts, progress_callback=show_progress)
    print()  # Newline after progress bar

    # Store in ChromaDB
    print("\nStoring in ChromaDB...")
    ids = []
    metadatas = []
    documents = []

    for i, chunk in enumerate(all_chunks):
        chunk_id = f"{chunk.source_file}_{chunk.header_level}_{chunk.chunk_index}_{i}"
        ids.append(chunk_id)
        metadatas.append({
            "source_file": chunk.source_file,
            "section_path": chunk.section_path,
            "header": chunk.header,
            "header_level": chunk.header_level,
            "chunk_index": chunk.chunk_index,
            "line_start": chunk.line_start,
            "line_end": chunk.line_end
        })
        documents.append(chunk.content)

    # Add to collection in batches
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        end = min(i + batch_size, len(ids))
        collection.add(
            ids=ids[i:end],
            embeddings=embeddings[i:end],
            metadatas=metadatas[i:end],
            documents=documents[i:end]
        )
        sys.stdout.write(f"\r  Stored {end}/{len(ids)} chunks")
        sys.stdout.flush()

    print()  # Newline after progress

    stats["chunks_created"] = len(all_chunks)

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Ingest markdown documentation into ChromaDB"
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Delete existing collection and rebuild from scratch"
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=None,
        help="Directory containing markdown files (default: Documentation/verified/)"
    )
    parser.add_argument(
        "--single",
        type=str,
        default=None,
        help="Process only this single file"
    )

    args = parser.parse_args()

    # Get paths
    docs_dir = args.docs_dir if args.docs_dir else get_docs_path()
    db_path = get_db_path()

    print("=" * 60)
    print("Vector Database Ingestion Pipeline")
    print("=" * 60)
    print(f"Documentation: {docs_dir}")
    print(f"Database: {db_path}")
    print(f"Rebuild: {args.rebuild}")
    if args.single:
        print(f"Single file: {args.single}")

    # Run ingestion
    stats = ingest_documents(
        docs_dir=docs_dir,
        db_path=db_path,
        rebuild=args.rebuild,
        single_file=args.single
    )

    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Files processed: {stats['files_processed']}")
    print(f"Chunks created:  {stats['chunks_created']}")
    if stats['errors']:
        print(f"Errors:          {len(stats['errors'])}")
        for error in stats['errors']:
            print(f"  - {error}")

    print("\nIngestion complete!")


if __name__ == "__main__":
    main()

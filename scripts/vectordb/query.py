#!/usr/bin/env python3
"""CLI query interface for the vector database."""

import argparse
import json
import sys
from pathlib import Path

import chromadb

from config import COLLECTION_NAME, get_db_path
from ollama_embed import OllamaConnectionError, OllamaEmbedder, OllamaModelError


def query_database(
    query_text: str,
    top_k: int = 5,
    file_filter: str = None,
    verbose: bool = False
) -> list:
    """
    Query the vector database.

    Args:
        query_text: The search query
        top_k: Number of results to return
        file_filter: Optional source file filter
        verbose: Show additional details

    Returns:
        List of result dicts with score, content, metadata
    """
    db_path = get_db_path()

    if not db_path.exists():
        print("ERROR: Database not found. Run rebuild.sh or ingest.py first.")
        sys.exit(1)

    # Connect to embedder
    if verbose:
        print("Connecting to Ollama...")
    try:
        embedder = OllamaEmbedder()
    except OllamaConnectionError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except OllamaModelError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Generate query embedding
    if verbose:
        print("Generating query embedding...")
    query_embedding = embedder.embed(query_text)

    # Connect to ChromaDB
    if verbose:
        print("Querying database...")
    client = chromadb.PersistentClient(path=str(db_path))

    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except ValueError:
        print(f"ERROR: Collection '{COLLECTION_NAME}' not found. Run rebuild.sh first.")
        sys.exit(1)

    # Build query
    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"]
    }

    if file_filter:
        query_params["where"] = {"source_file": file_filter}

    # Execute query
    results = collection.query(**query_params)

    # Format results
    formatted = []
    if results["ids"] and results["ids"][0]:
        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i] if results["distances"] else None
            # Convert distance to similarity score (cosine: 1 - distance)
            score = 1 - distance if distance is not None else None

            formatted.append({
                "rank": i + 1,
                "score": score,
                "source_file": results["metadatas"][0][i]["source_file"],
                "section_path": results["metadatas"][0][i]["section_path"],
                "header": results["metadatas"][0][i]["header"],
                "line_start": results["metadatas"][0][i]["line_start"],
                "line_end": results["metadatas"][0][i]["line_end"],
                "content": results["documents"][0][i]
            })

    return formatted


def print_results(results: list, show_content: bool = True) -> None:
    """Pretty-print query results."""
    if not results:
        print("No results found.")
        return

    print(f"\nFound {len(results)} results:\n")
    print("-" * 70)

    for result in results:
        print(f"\n[{result['rank']}] Score: {result['score']:.4f}")
        print(f"    Source: {result['source_file']} (lines {result['line_start']}-{result['line_end']})")
        print(f"    Section: {result['section_path']}")

        if show_content:
            # Truncate content for display
            content = result['content']
            if len(content) > 500:
                content = content[:500] + "..."
            print(f"\n    Content:\n    {'-' * 40}")
            # Indent content
            for line in content.split('\n')[:10]:
                print(f"    {line}")
            if content.count('\n') > 10:
                print("    ...")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Query the vector database for documentation"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="The search query text"
    )
    parser.add_argument(
        "-k", "--top-k",
        type=int,
        default=5,
        help="Number of results to return (default: 5)"
    )
    parser.add_argument(
        "-f", "--file",
        type=str,
        default=None,
        help="Filter results to specific source file"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show verbose output"
    )
    parser.add_argument(
        "--no-content",
        action="store_true",
        help="Don't show content in results"
    )

    args = parser.parse_args()

    if not args.query:
        parser.print_help()
        print("\nExample: python3 query.py 'How does the boot process work?'")
        sys.exit(1)

    results = query_database(
        query_text=args.query,
        top_k=args.top_k,
        file_filter=args.file,
        verbose=args.verbose
    )

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_results(results, show_content=not args.no_content)


if __name__ == "__main__":
    main()

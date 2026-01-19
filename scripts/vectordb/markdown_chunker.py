"""Markdown document chunker with header-based parsing."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from config import MAX_CHUNK_CHARS, OVERLAP_CHARS


@dataclass
class Chunk:
    """Represents a chunk of a markdown document."""
    content: str
    source_file: str
    section_path: str
    header: str
    header_level: int
    chunk_index: int
    line_start: int
    line_end: int


class MarkdownChunker:
    """Parser for chunking markdown documents by headers."""

    HEADER_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    def __init__(
        self,
        max_chunk_chars: int = MAX_CHUNK_CHARS,
        overlap_chars: int = OVERLAP_CHARS
    ):
        """
        Initialize the chunker.

        Args:
            max_chunk_chars: Maximum characters per chunk
            overlap_chars: Characters to overlap between chunks
        """
        self.max_chunk_chars = max_chunk_chars
        self.overlap_chars = overlap_chars

    def chunk_file(self, path: Path) -> List[Chunk]:
        """
        Chunk a markdown file by headers.

        Args:
            path: Path to the markdown file

        Returns:
            List of Chunk objects
        """
        content = path.read_text(encoding='utf-8')
        source_file = path.name

        # Parse headers with their positions
        headers = self._parse_headers(content)

        if not headers:
            # No headers found, treat entire file as one chunk
            return self._create_chunks_from_section(
                content=content,
                source_file=source_file,
                section_path="",
                header="(No header)",
                header_level=0,
                line_start=1
            )

        chunks = []
        lines = content.split('\n')

        # Process each section
        for i, (level, header_text, start_pos) in enumerate(headers):
            # Find end position (start of next header at same or higher level, or end of file)
            end_pos = len(content)
            for j in range(i + 1, len(headers)):
                next_level, _, next_pos = headers[j]
                if next_level <= level:
                    end_pos = next_pos
                    break
                # Also break at any header for content extraction
                end_pos = next_pos
                break

            # Extract section content
            section_content = content[start_pos:end_pos].strip()

            # Calculate line numbers
            line_start = content[:start_pos].count('\n') + 1

            # Build section path
            section_path = self._build_section_path(headers[:i+1], level)

            # Create chunks from this section
            section_chunks = self._create_chunks_from_section(
                content=section_content,
                source_file=source_file,
                section_path=section_path,
                header=header_text,
                header_level=level,
                line_start=line_start
            )
            chunks.extend(section_chunks)

        return chunks

    def _parse_headers(self, content: str) -> List[Tuple[int, str, int]]:
        """
        Parse headers from markdown content.

        Returns:
            List of (level, header_text, start_position) tuples
        """
        headers = []
        for match in self.HEADER_PATTERN.finditer(content):
            level = len(match.group(1))  # Count # symbols
            header_text = match.group(2).strip()
            start_pos = match.start()
            headers.append((level, header_text, start_pos))
        return headers

    def _build_section_path(
        self,
        headers_so_far: List[Tuple[int, str, int]],
        current_level: int
    ) -> str:
        """
        Build a hierarchical section path from headers.

        Example: "Phase 2 > Network Detection > Step 2.1"
        """
        if not headers_so_far:
            return ""

        # Build path by tracking the header stack
        path_parts = []
        stack = []  # (level, header_text)

        for level, header_text, _ in headers_so_far:
            # Pop headers that are at the same or lower level
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, header_text))

        # Extract just the header texts
        path_parts = [h[1] for h in stack]

        return " > ".join(path_parts)

    def _create_chunks_from_section(
        self,
        content: str,
        source_file: str,
        section_path: str,
        header: str,
        header_level: int,
        line_start: int
    ) -> List[Chunk]:
        """
        Create chunks from a section, splitting if oversized.
        """
        if len(content) <= self.max_chunk_chars:
            line_end = line_start + content.count('\n')
            return [Chunk(
                content=content,
                source_file=source_file,
                section_path=section_path,
                header=header,
                header_level=header_level,
                chunk_index=0,
                line_start=line_start,
                line_end=line_end
            )]

        # Split oversized section
        parts = self._split_oversized_section(content)
        chunks = []

        current_line = line_start
        for i, part in enumerate(parts):
            # Add overlap from previous chunk
            if i > 0 and chunks:
                part = self._add_overlap(chunks[-1].content, part)

            line_count = part.count('\n')
            chunks.append(Chunk(
                content=part,
                source_file=source_file,
                section_path=section_path,
                header=header,
                header_level=header_level,
                chunk_index=i,
                line_start=current_line,
                line_end=current_line + line_count
            ))
            current_line += content[len(part) - len(part.lstrip()):].count('\n')

        return chunks

    def _split_oversized_section(self, content: str) -> List[str]:
        """
        Split oversized content at paragraph boundaries.
        """
        # Split at double newlines (paragraph boundaries)
        paragraphs = re.split(r'\n\n+', content)

        parts = []
        current_part = ""

        for para in paragraphs:
            if len(current_part) + len(para) + 2 <= self.max_chunk_chars:
                if current_part:
                    current_part += "\n\n" + para
                else:
                    current_part = para
            else:
                if current_part:
                    parts.append(current_part)

                # Handle single paragraphs that are too large
                if len(para) > self.max_chunk_chars:
                    # Split at sentence boundaries
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    current_part = ""
                    for sentence in sentences:
                        if len(current_part) + len(sentence) + 1 <= self.max_chunk_chars:
                            if current_part:
                                current_part += " " + sentence
                            else:
                                current_part = sentence
                        else:
                            if current_part:
                                parts.append(current_part)
                            current_part = sentence
                else:
                    current_part = para

        if current_part:
            parts.append(current_part)

        return parts

    def _add_overlap(self, previous_content: str, current_content: str) -> str:
        """
        Add overlap from the end of previous chunk to the start of current.
        """
        if len(previous_content) <= self.overlap_chars:
            overlap = previous_content
        else:
            # Find a good break point (word boundary)
            overlap_start = len(previous_content) - self.overlap_chars
            # Find the next space after overlap_start
            space_pos = previous_content.find(' ', overlap_start)
            if space_pos != -1:
                overlap = previous_content[space_pos + 1:]
            else:
                overlap = previous_content[-self.overlap_chars:]

        return f"[...] {overlap}\n\n{current_content}"

import math
import re
from typing import List
from dataclasses import dataclass
from .base_chunker import BaseChunker


@dataclass
class Chunk:
    text: str
    delimiter: str | None

    def get_len(self) -> int:
        """Get total length including delimiter"""
        if self.delimiter is None:
            return len(self.text)
        return len(self.text) + len(self.delimiter)

    def get_text_len(self) -> int:
        """Get length of text only, excluding delimiter"""
        return len(self.text)


class TextChunker(BaseChunker):
    """
    Chunk text into chunks of a specified size using a tiered approach.
    Only applies more fine-grained chunking strategies when necessary.
    """

    def __init__(self, max_chunk_size: int = 500):
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str) -> List[str]:
        """
        Chunk text using a tiered approach:
        1. Split by paragraph (double newlines)
        2. If needed, split by single newlines
        3. If needed, split by sentences
        4. If needed, split by delimiters (commas, colons, etc.)
        5. If needed, split by spaces
        6. If needed, split by character count
        """
        if not text:
            return []

        # Start with the entire text as one chunk
        chunks = [Chunk(text, None)]

        # Apply increasingly fine-grained chunking as needed
        chunks = self._refine_chunks(chunks)

        text_chunks = []
        for chunk in chunks:
            text_chunk = chunk.text
            # Only append the delimiter if it is not None
            if chunk.delimiter is not None:
                text_chunk += chunk.delimiter
            text_chunks.append(text_chunk)

        return text_chunks

    def _refine_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """Apply increasingly fine-grained chunking methods as needed, with recombination."""
        chunks = self._refine_by_paragraphs(chunks)
        chunks = self._refine_by_newlines(chunks)
        chunks = self._refine_by_sentences(chunks)
        chunks = self._refine_by_delimiters(chunks)
        chunks = self._refine_by_spaces(chunks)
        chunks = self._refine_by_characters(chunks)
        return chunks

    def _recombine_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """Recombine adjacent chunks using their delimiters until they exceed max_chunk_size."""
        if not chunks:
            return []

        recombined = []
        current_chunk = Chunk(chunks[0].text, chunks[0].delimiter)

        for i in range(1, len(chunks)):
            next_chunk = chunks[i]
            potential_chunk = Chunk(current_chunk.text + (current_chunk.delimiter or "") + next_chunk.text, next_chunk.delimiter)

            if potential_chunk.get_len() > self.max_chunk_size:
                recombined.append(current_chunk)
                current_chunk = next_chunk
            else:
                current_chunk = potential_chunk

        # Add the last chunk
        recombined.append(current_chunk)

        return recombined

    def _refine_by_paragraphs(self, chunks: List[Chunk]) -> List[Chunk]:
        """Split chunks by paragraphs if they're too large."""
        refined = []
        for chunk in chunks:
            if chunk.get_len() <= self.max_chunk_size:
                refined.append(chunk)
                continue

            para_chunks = chunk.text.split("\n\n")
            refined.extend(Chunk(c, "\n\n") for c in para_chunks[:-1])
            refined.append(Chunk(para_chunks[-1], chunk.delimiter))
        return self._recombine_chunks(refined)

    def _refine_by_newlines(self, chunks: List[Chunk]) -> List[Chunk]:
        """Split chunks by newlines if they're too large."""
        refined = []
        for chunk in chunks:
            if chunk.get_len() <= self.max_chunk_size:
                refined.append(chunk)
                continue

            line_chunks = chunk.text.split("\n")
            refined.extend(Chunk(c, "\n") for c in line_chunks[:-1])
            refined.append(Chunk(line_chunks[-1], chunk.delimiter))
        return self._recombine_chunks(refined)

    def _refine_by_sentences(self, chunks: List[Chunk]) -> List[Chunk]:
        """Split chunks by sentences if they're too large."""
        refined = []
        for chunk in chunks:
            if chunk.get_len() <= self.max_chunk_size:
                refined.append(chunk)
                continue

            # Split after a sentence-ending punctuation followed by a single space
            sentence_chunks = re.split(r'(?<=[.!?])\s', chunk.text)

            # For all chunks except the last one, extract their delimiter
            for sentence in sentence_chunks[:-1]:
                # The sentence already ends with punctuation due to the split pattern
                refined.append(Chunk(sentence, " "))

            # Handle the last chunk with the original chunk's delimiter
            refined.append(Chunk(sentence_chunks[-1], chunk.delimiter))

        return self._recombine_chunks(refined)

    def _refine_by_delimiters(self, chunks: List[Chunk]) -> List[Chunk]:
        """Split chunks by delimiters if they're too large."""
        refined = []
        for chunk in chunks:
            if chunk.get_len() <= self.max_chunk_size:
                refined.append(chunk)
                continue

            last_end = 0
            chunk_refined = []

            for match in re.finditer(r'(,\s+|:\s+|;\s+)', chunk.text):
                text = chunk.text[last_end:match.start()]
                if text:
                    chunk_refined.append(Chunk(text.strip(), match.group()))
                last_end = match.end()

            final_text = chunk.text[last_end:]
            if final_text:
                chunk_refined.append(Chunk(final_text.strip(), chunk.delimiter))
            elif chunk_refined:
                last_chunk = chunk_refined[-1]
                chunk_refined[-1] = Chunk(last_chunk.text, chunk.delimiter)

            refined.extend(chunk_refined)
        return self._recombine_chunks(refined)

    def _refine_by_spaces(self, chunks: List[Chunk]) -> List[Chunk]:
        """Split chunks by spaces if they're too large."""
        refined = []
        for chunk in chunks:
            if chunk.get_len() <= self.max_chunk_size:
                refined.append(chunk)
                continue

            space_chunks = chunk.text.split(" ")
            refined.extend(Chunk(c, " ") for c in space_chunks[:-1])
            refined.append(Chunk(space_chunks[-1], chunk.delimiter))
        return self._recombine_chunks(refined)

    def _refine_by_characters(self, chunks: List[Chunk]) -> List[Chunk]:
        """Split chunks by character count if they're too large."""
        refined = []
        for chunk in chunks:
            if chunk.get_len() <= self.max_chunk_size:
                refined.append(chunk)
                continue

            char_chunks = [chunk.text[i:i + self.max_chunk_size]
                          for i in range(0, len(chunk.text), self.max_chunk_size)]
            refined.extend(Chunk(c, "") for c in char_chunks[:-1])

            # Handle the last chunk carefully with its delimiter
            last_chunk = char_chunks[-1]
            if len(last_chunk) + len(chunk.delimiter or "") > self.max_chunk_size:
                # Split the last somewhat evenly, distributing the delimiter length
                delimiter_len = len(chunk.delimiter or "")
                first_part_len = min(len(last_chunk) // 2 + delimiter_len, len(last_chunk))

                refined.append(Chunk(last_chunk[:first_part_len], ""))
                refined.append(Chunk(last_chunk[first_part_len:], chunk.delimiter))

            else:
                refined.append(Chunk(last_chunk, chunk.delimiter))

        return self._recombine_chunks(refined)
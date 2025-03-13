from .base_chunker import BaseChunker
from .text_chunker import TextChunker, Chunk

# Create an instance of TextChunker to export as chunker
chunker = TextChunker()

__all__ = ["BaseChunker", "TextChunker", "Chunk", "chunker"]
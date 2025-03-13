from abc import ABC, abstractmethod
from typing import List


class BaseChunker(ABC):
    """
    Abstract base class for text chunking strategies.
    """

    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        """
        Split text into chunks according to the chunking strategy.

        Args:
            text: The text to chunk

        Returns:
            A list of text chunks
        """
        pass
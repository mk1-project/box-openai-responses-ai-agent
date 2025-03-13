import os
import json
import requests
import logging
import traceback
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Highlights API key from environment variables
HIGHLIGHTS_API_KEY = os.getenv("HIGHLIGHTS_API_KEY")


class HighlightsAPI:
    """
    Client for interacting with the MK1 Highlights API.
    """

    BASE_URL = "https://api.highlights.mk1.ai/search"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Highlights API client.

        Args:
            api_key: Highlights API key (defaults to environment variable)
        """
        self.api_key = api_key or HIGHLIGHTS_API_KEY

        if not self.api_key or self.api_key == "your_highlights_api_key_here":
            logging.warning("Highlights API key is not properly set. The Highlights functionality will not work correctly.")
            self.api_key = "missing_api_key"

    def get_highlights(self, text: str, query: str, max_highlights: int = 5) -> List[Dict[str, Any]]:
        """
        Get highlights from text based on a query.

        Args:
            text: The text to analyze
            query: The query to find relevant highlights for
            max_highlights: Maximum number of highlights to return

        Returns:
            List of highlights with text and relevance score
        """
        if not text or not text.strip():
            logging.warning("Empty text provided to get_highlights")
            return []

        if not query or not query.strip():
            logging.warning("Empty query provided to get_highlights")
            return []

        if self.api_key == "missing_api_key":
            # Simulate highlights for testing when API key is missing
            logging.warning("Using simulated highlights due to missing API key")
            return [{"text": f"Simulated highlight for query: {query}", "relevance": 0.95}]

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }

        payload = {
            "query": query,
            "chunk_txts": [text],
            "top_n": max_highlights,
            "true_order": True
        }

        try:
            logging.info(f"Sending request to Highlights API with query: {query}")
            response = requests.post(
                self.BASE_URL,
                headers=headers,
                json=payload,
                timeout=30  # Add timeout to prevent hanging
            )

            if response.status_code != 200:
                logging.error(f"Highlights API error: {response.status_code} - {response.text}")
                return []

            result = response.json()
            logging.info(f"Received response from Highlights API: {result}")

            # Format according to the actual API response structure
            highlights = []
            results = result.get("results", [])
            for res in results:
                highlights.append({
                    "text": res["chunk_txt"],
                    "relevance": res["chunk_score"]
                })

            return highlights
        except requests.exceptions.RequestException as e:
            logging.error(f"Error getting highlights: {e}\nTraceback: {traceback.format_exc()}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error in get_highlights: {e}\nTraceback: {traceback.format_exc()}")
            return []

    def get_highlights_from_chunks(self, chunks: List[str], query: str, max_highlights_per_chunk: int = 10) -> List[Dict[str, Any]]:
        """
        Get highlights from multiple text chunks based on a query.

        Args:
            chunks: List of text chunks to analyze
            query: The query to find relevant highlights for
            max_highlights_per_chunk: Maximum number of highlights to return per chunk

        Returns:
            List of highlights with text and relevance score
        """
        if not chunks:
            logging.warning("Empty chunks provided to get_highlights_from_chunks")
            return []

        if not query or not query.strip():
            logging.warning("Empty query provided to get_highlights_from_chunks")
            return []

        if self.api_key == "missing_api_key":
            # Simulate highlights for testing when API key is missing
            logging.warning("Using simulated highlights due to missing API key")
            return [{"text": f"Simulated highlight for query: {query} (chunk {i})", "relevance": 0.95 - (i * 0.05), "chunk_index": i}
                    for i in range(min(5, len(chunks)))]

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }

        payload = {
            "query": query,
            "chunk_txts": chunks,
            "top_n": max_highlights_per_chunk,
            "true_order": True
        }

        try:
            logging.info(f"Sending request to Highlights API with query: {query}")
            response = requests.post(
                self.BASE_URL,
                headers=headers,
                json=payload,
                timeout=60  # Longer timeout for larger request
            )

            if response.status_code != 200:
                logging.error(f"Highlights API error: {response.status_code} - {response.text}")
                return []

            result = response.json()
            logging.info(f"Received response from Highlights API: {result}")

            # Process the results based on the actual API response structure
            highlights = []
            results = result.get("results", [])
            if not results:
                logging.warning("No results returned from Highlights API")
                return []

            for res in results:
                highlights.append({
                    "text": res["chunk_txt"],
                    "relevance": res["chunk_score"],
                    "chunk_index": res["original_index"]
                })

            return highlights
        except requests.exceptions.RequestException as e:
            logging.error(f"Error getting highlights: {e}\nTraceback: {traceback.format_exc()}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error in get_highlights_from_chunks: {e}\nTraceback: {traceback.format_exc()}")
            return []
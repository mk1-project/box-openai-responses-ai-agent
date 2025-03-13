import os
import tempfile
from typing import Optional
from box_agent.lib.box_api import box_file_text_extract

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None


class PDFTextExtractor:
    """
    Extracts text from PDF files.
    """

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> Optional[str]:
        """
        Extract text from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text or None if extraction failed
        """
        if PyPDF2 is None:
            raise ImportError("PyPDF2 is required for PDF text extraction. Install it with 'pip install PyPDF2'.")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""

                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n\n"

                return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None

    @staticmethod
    def extract_text_from_box_file(file_id: str, box_client) -> Optional[str]:
        """
        Extract text from a Box PDF file.

        Args:
            file_id: Box file ID
            box_client: Box client instance

        Returns:
            Extracted text or None if extraction failed
        """
        try:
            # Use the box_file_text_extract function to get the text content directly
            text = box_file_text_extract(box_client, file_id)
            # Clean the text by removing extra whitespace and normalizing line endings
            if text:
                text = ' '.join(text.split())  # Remove extra whitespace
                text = text.replace('\t', ' ')  # Replace tabs with spaces
                text = text.strip()  # Remove leading/trailing whitespace
            return text
        except Exception as e:
            print(f"Error extracting text from Box PDF: {e}")
            return None
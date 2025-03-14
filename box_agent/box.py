from typing import List, Union
from box_agent.lib.box_api import (
    box_search,
    box_file_text_extract,
    box_file_ai_ask,
    box_locate_folder_by_name,
    box_folder_list_content,
)
from box_agent.lib.box_auth import BoxAuth
from box_agent.highlights_api import HighlightsAPI
from box_agent.chunking import chunker
from box_agent.pdf_extractor import PDFTextExtractor
import logging
from box_sdk_gen import (
    File,
    Folder,
)
import json

from agents import function_tool


@function_tool
async def file_search(
    query: str,
    file_extensions: List[str] | None = None,
    where_to_look_for_query: List[str] | None = None,
    ancestor_folder_ids: List[str] | None = None,
) -> str:
    """
    Search for files in Box with the given query.

    Args:
        query (str): The query to search for.
        file_extensions (List[str]): The file extensions to search for, for example *.pdf
        content_types (List[SearchForContentContentTypes]): where to look for the information, possible values are:
            NAME
            DESCRIPTION,
            FILE_CONTENT,
            COMMENTS,
            TAG,
        ancestor_folder_ids (List[str]): The ancestor folder IDs to search in.
    return:
        str: The search results.
    """
    # # Convert the where to look for query to content types
    # content_types: List[SearchForContentContentTypes] = []
    # if where_to_look_for_query:
    #     for content_type in where_to_look_for_query:
    #         content_type = content_type.upper()
    #         content_types.append(SearchForContentContentTypes[content_type])

    # Search for files with the query
    search_results = box_search(
        BoxAuth().get_client(),
        query,
        file_extensions,
        # content_types,
        ancestor_folder_ids,
    )

    # Return the "id", "name", "description" of the search results
    search_results = [
        f"{file.name} (id:{file.id})"
        + (f" {file.description}" if file.description else "")
        for file in search_results
    ]

    return "\n".join(search_results)


@function_tool
async def ask_box(file_id: str, prompt: str) -> str:
    """
    Ask box ai about a file in Box.

    Type: function

    Args:
        file_id (str): The ID of the file to read.
        prompt (str): The prompt to ask the AI.
        type: function
    return:
        str: The text content of the file.
    """

    # check if file id isn't a string and convert to a string
    if not isinstance(file_id, str):
        file_id = str(file_id)

    # ai_agent = box_ai_agent_ask()
    response = box_file_ai_ask(
        BoxAuth().get_client(),
        file_id,
        prompt=prompt,
    )

    return response


@function_tool
async def get_text_from_file(file_id: str) -> str:
    """
    Read the text content of a file in Box.

        Args:
            file_id (str): The ID of the file to read.
        return:
            str: The text content of the file.
    """
    # log parameters and its type
    logging.info(f"file_id: {file_id}, type: {type(file_id)}")

    # check if file id isn't a string and convert to a string
    if not isinstance(file_id, str):
        file_id = str(file_id)

    response = box_file_text_extract(BoxAuth().get_client(), file_id)

    return response


@function_tool
async def box_search_folder_by_name(folder_name: str) -> str:
    """
    Locate a folder in Box by its name.

    Args:
        folder_name (str): The name of the folder to locate.
    return:
        str: The folder ID.
    """

    search_results = box_locate_folder_by_name(BoxAuth().get_client(), folder_name)

    # Return the "id", "name", "description" of the search results
    search_results = [f"{folder.name} (id:{folder.id})" for folder in search_results]

    return "\n".join(search_results)


@function_tool
async def box_list_folder_content_by_folder_id(
    folder_id: str, is_recursive: bool
) -> str:
    """
    List the content of a folder in Box by its ID.

    Args:
        folder_id (str): The ID of the folder to list the content of.
        is_recursive (bool): Whether to list the content recursively.

    return:
        str: The content of the folder in a json string format, including the "id", "name", "type", and "description".
    """

    # check if file id isn't a string and convert to a string
    if not isinstance(folder_id, str):
        folder_id = str(folder_id)

    response: List[Union[File, Folder]] = box_folder_list_content(
        BoxAuth().get_client(), folder_id, is_recursive
    )
    # Convert the response to a json string

    response = [
        {
            "id": item.id,
            "name": item.name,
            "type": item.type,
            "description": item.description if hasattr(item, "description") else None,
        }
        for item in response
    ]
    return json.dumps(response)


@function_tool
async def get_highlights_from_file(file_id: str, query: str, max_highlights: int) -> str:
    """
    Extract text from a file, chunk it, and get highlights based on a query using MK1 Highlights API.

    Args:
        file_id: The Box file ID
        query: The query to find relevant highlights for
        max_highlights: Maximum number of highlights to return

    Returns:
        A string containing the most relevant highlights from the file
    """
    try:
        # Get Box client
        box_client = BoxAuth().get_client()
        if box_client is None:
            return "Error: Box authentication failed. Please check your Box credentials in the .env file."

        file_info = box_client.files.get_file_by_id(file_id)
        file_name = file_info.name
        logging.debug(f"Processing file: {file_name} (ID: {file_id})")

        # Extract text from the file
        if file_name.lower().endswith('.pdf'):
            # For PDF files, use the PDF extractor
            logging.debug(f"Extracting text from PDF file: {file_name}")
            text = PDFTextExtractor.extract_text_from_box_file(file_id, box_client)
        else:
            # For other files, use the Box API
            logging.debug(f"Extracting text from non-PDF file: {file_name}")
            text = await box_file_text_extract(file_id)

        if not text:
            logging.error(f"Failed to extract text from file {file_name} (ID: {file_id})")
            return f"Failed to extract text from file {file_name} (ID: {file_id})."

        # Log text length
        logging.debug(f"Extracted {len(text)} characters of text from {file_name}")

        # Chunk the text
        chunks = chunker.chunk(text)
        logging.debug(f"Created {len(chunks)} chunks from {file_name}")

        # Get highlights from chunks
        logging.debug(f"Requesting highlights for query: '{query}'")
        highlights = HighlightsAPI().get_highlights_from_chunks(chunks, query)

        # Limit the number of highlights
        highlights = highlights[:max_highlights]
        logging.debug(f"Received {len(highlights)} highlights from MK1 Highlights API")

        if not highlights:
            return f"No relevant highlights found in file {file_name} (ID: {file_id}) for query: {query}"

        # Format the highlights
        result = f"Highlights from {file_name} (ID: {file_id}) for query: {query}\n\n"

        for i, highlight in enumerate(highlights, 1):
            result += f"{i}. {highlight['text']}\n"

        return result

    except Exception as e:
        logging.error(f"Error getting highlights: {e}")
        return f"Error getting highlights from file (ID: {file_id}): {str(e)}"

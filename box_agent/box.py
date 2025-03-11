from typing import Any, AsyncIterator, List, Optional, Union, cast  # , Optional, cast
from box_agent.lib.box_api import (
    box_search,
    box_file_text_extract,
    box_file_ai_ask,
    box_locate_folder_by_name,
    box_file_ai_extract,
    box_folder_list_content,
    box_ai_agent_ask,
    box_ai_agent_extract,
)
from box_agent.lib.box_auth import BoxAuth

import logging
from box_sdk_gen import (
    SearchForContentContentTypes,
    File,
    Folder,
    BoxClient,
    AiSingleAgentResponseFull,
)
import json

from agents import Agent, function_tool


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

    ai_agent = box_ai_agent_ask()
    response = box_file_ai_ask(
        BoxAuth().get_client(), file_id, prompt=prompt, ai_agent=ai_agent
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

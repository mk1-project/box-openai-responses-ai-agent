import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

from openai.types.responses import ResponseContentPartDoneEvent, ResponseTextDeltaEvent

from agents import Agent, Runner, TResponseInputItem
from agents.tool import WebSearchTool

from box_agent.box import (
    file_search,
    ask_box,
    get_text_from_file,
    box_search_folder_by_name,
    box_list_folder_content_by_folder_id,
    get_highlights_from_file,
)

from box_agent.lib.formatting import strip_markdown
from box_agent.lib.box_auth import BoxAuth

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and above to reduce console clutter
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("error.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Set httpx logger to ERROR level to suppress HTTP request logs
logging.getLogger("httpx").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

DEFAULT_MAX_TURNS = 100

# Check if Highlights API key is set
HIGHLIGHTS_API_KEY = os.getenv("HIGHLIGHTS_API_KEY")
if not HIGHLIGHTS_API_KEY:
    logger.warning("HIGHLIGHTS_API_KEY not found in environment variables. Highlights functionality will not work.")

# Check Box credentials
BOX_CLIENT_ID = os.getenv("BOX_CLIENT_ID")
BOX_CLIENT_SECRET = os.getenv("BOX_CLIENT_SECRET")
BOX_SUBJECT_ID = os.getenv("BOX_SUBJECT_ID")

if not BOX_CLIENT_ID or not BOX_CLIENT_SECRET or not BOX_SUBJECT_ID:
    logger.error("Box credentials are missing in .env file")
    print("⚠️ Box credentials are missing in .env file. Box functionality will not work.")
    print("Please check your .env file and make sure the following variables are set:")
    print("  - BOX_CLIENT_ID")
    print("  - BOX_CLIENT_SECRET")
    print("  - BOX_SUBJECT_TYPE")
    print("  - BOX_SUBJECT_ID")
    print("The agent will still run, but Box-related functionality will not work.\n")
else:
    # Try to authenticate with Box
    try:
        box_client = BoxAuth().get_client()
        if box_client:
            current_user = box_client.users.get_user_me()
            logger.info(f"Successfully authenticated with Box as: {current_user.name} (ID: {current_user.id})")
            print(f"✅ Successfully authenticated with Box as: {current_user.name} (ID: {current_user.id})")
        else:
            logger.error("Failed to initialize Box client")
            print("⚠️ Failed to initialize Box client. Box functionality will not work.")
    except Exception as e:
        logger.error(f"Box authentication failed: {e}")
        print("⚠️ Box authentication failed. Box functionality will not work.")
        print(f"Error: {str(e)}")
        print("Please check your Box credentials in the .env file.")

box_agent = Agent(
    name="Box Agent",
    instructions="""
    You are a very helpful agent. You are a financial expert.
    You have access to a number of tools from Box that allow you
    to search for files in Box either holistically or by set criteria.

    IMPORTANT WORKFLOW:
    1. When a user asks about a file, first use file_search to find the file and get its ID.
    2. Once you have the file ID, you can use other tools to work with the file.

    For large files, especially PDFs, you should use the get_highlights_from_file tool
    which will extract text, chunk it, and use the MK1 Highlights API to find the most
    relevant parts of the document based on the user's query. This is more efficient
    than trying to process the entire document at once.

    When using the get_highlights_from_file tool, you need to provide:
    - file_id: The ID of the file to analyze (you must get this from file_search first)
    - query: The user's query or what information they're looking for
    - max_highlights: The number of highlights to return (recommend using 5)

    If you encounter any errors with Box authentication or access, inform the user that
    there might be an issue with the Box credentials and suggest they check the error logs.

    If you encounter any other errors, provide clear explanations to the user and suggest
    alternative approaches. Your goal is to help the user find the information they need.
    """,
    tools=[
        file_search,
        ask_box,
        get_text_from_file,
        get_highlights_from_file,
        box_search_folder_by_name,
        box_list_folder_content_by_folder_id,
        WebSearchTool(),
    ],
)


async def main():
    print("\n🤖 Box Agent with MK1 Highlights Integration\n")
    print("This agent can search for files in Box, extract text, and use the MK1 Highlights API")
    print("to find the most relevant parts of documents based on your queries.\n")

    user_msg = input("How can I help you today:\n")
    agent = box_agent
    inputs: list[TResponseInputItem] = [{"content": user_msg, "role": "user"}]
    while True:
        try:
            result = Runner.run_streamed(
                agent,
                input=inputs,
                max_turns=DEFAULT_MAX_TURNS,
            )
            async for event in result.stream_events():
                if isinstance(event, ResponseTextDeltaEvent):
                    print(event.delta, end="", flush=True)
                elif isinstance(event, ResponseContentPartDoneEvent):
                    print("\n")

            answer = strip_markdown(result.final_output)
            answer = answer.replace("\n\n", "\n")
            print(f"{answer}\n")

            inputs = result.to_input_list()
            print()

            user_msg = input("Follow up:\n")

            inputs.append({"content": user_msg, "role": "user"})
        except Exception as e:
            logger.error(f"Error running agent: {e}")
            print(f"\n⚠️ Error: {str(e)}")
            print("Please check the error.log file for more details.")
            user_msg = input("\nFollow up (or type 'exit' to quit):\n")
            if user_msg.lower() == 'exit':
                break
            inputs.append({"content": user_msg, "role": "user"})


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting Box Agent. Goodbye! 👋")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        print(f"\n⚠️ Unhandled exception: {str(e)}")
        print("Please check the error.log file for more details.")

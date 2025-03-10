import asyncio

from agents.tool import WebSearchTool
import logging

from openai.types.responses import ResponseContentPartDoneEvent, ResponseTextDeltaEvent

from agents import Agent, Runner, TResponseInputItem

from box_agent.box import (
    file_search,
    ask_box,
    get_text_from_file,
    box_search_folder_by_name,
    box_list_folder_content_by_folder_id,
)

logger = logging.getLogger(__name__)
logging.basicConfig(filename="error.log", level=logging.DEBUG)

box_agent = Agent(
    name="Box Agent",
    instructions="""
    You are a very helpful agent. You are a financial expert. 
    You have access to a number of tools from Box that allow you
    to search for files in Box either holistically or by set criteria.
    You can also ask Box AI to answer questions about the files or you
    can retriever the text from the files. Your goal is to help the user
    find the information they need.
    """,
    tools=[
        file_search,
        ask_box,
        get_text_from_file,
        box_search_folder_by_name,
        box_list_folder_content_by_folder_id,
        WebSearchTool(),
    ],
)


async def main():
    msg = input("How can I help you today:\n")

    """
    Look for all files in the 'Earnings Reports Q4' folder in Box. Analyze
    these files and write a report about the major trends facing technology 
    companies in Q4"""
    agent = box_agent
    inputs: list[TResponseInputItem] = [{"content": msg, "role": "user"}]
    while True:
        result = Runner.run_streamed(
            agent,
            input=inputs,
        )
        async for event in result.stream_events():
            if isinstance(event, ResponseTextDeltaEvent):
                print(event.delta, end="", flush=True)
            elif isinstance(event, ResponseContentPartDoneEvent):
                print("\n")

        # print(f"{result.to_input_list()}\n")
        print(f"{result.final_output}\n")

        inputs = result.to_input_list()
        print("\n==================================================================")

        user_msg = input("Follow up:\n")
        inputs.append({"content": user_msg, "role": "user"})


if __name__ == "__main__":
    asyncio.run(main())

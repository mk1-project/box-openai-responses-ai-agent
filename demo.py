import asyncio
import time

import logging


from openai.types.responses import ResponseContentPartDoneEvent, ResponseTextDeltaEvent

from agents import Agent, Runner, TResponseInputItem
from agents.tool import WebSearchTool

from box_agent.box import (
    file_search,
    ask_box,
    get_text_from_file,
    box_search_folder_by_name,
    box_list_folder_content_by_folder_id,
)

from box_agent.lib.formatting import strip_markdown

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


def slow_print(text: str, delay=0.1):
    """Prints a string character by character with a delay."""
    # remove any \n characters
    text = text.replace("\n", "")
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()  # Add a newline at the end


async def main():
    prompt_a = (
        "List out the companies in the Q4 tech earnings folder I have research on"
    )
    prompt_b = "Generate a comprehensive report that analyzes the top tech trends facing these companies in Q4"
    prompt_c = "What are the biggest AI datacenter build-outs mentioned in my research? After analyzing my research, supplement my data with the latest headlines regarding AI datacenter build-outs in the news. Please provide links for insights not in my research."

    prompts = [prompt_a, prompt_b, prompt_c]

    agent = box_agent

    inputs: list[TResponseInputItem] = []

    print("How can I help you today:")
    for prompt in prompts:
        time.sleep(5)
        slow_print(f"{prompt}", delay=0.15)
        user_msg = prompt
        inputs.append({"content": user_msg, "role": "user"})
        result = Runner.run_streamed(
            agent,
            input=inputs,
        )
        async for event in result.stream_events():
            if isinstance(event, ResponseTextDeltaEvent):
                print(event.delta, end="", flush=True)
            elif isinstance(event, ResponseContentPartDoneEvent):
                print("\n")

        answer = strip_markdown(result.final_output)
        answer.replace("\n\n", "\n")
        # split the answer into a list of lines
        lines = answer.split("\n")
        print("\n")
        # print the lines one by one with a delay
        for line in lines:
            slow_print(line, delay=0.02)

        print("\nFollow up:")


if __name__ == "__main__":
    asyncio.run(main())

from openai.types.responses import ResponseTextDeltaEvent
import asyncio
import os
from dotenv import load_dotenv
import random
from agents import Agent, ItemHelpers, Runner, function_tool











load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")

@function_tool
def how_many_jokes() -> int:
    return random.randint(1, 10)

joker_agent = Agent(
    name="Joker_agent",
    instructions="First call the `how_many_jokes` tool, then tell that many jokes.",
    model="gpt-4o-mini",
    tools=[how_many_jokes],
)
agent=Agent(
    name="Joker",
    instructions="You are a helpful assistant", 
    model="gpt-4o-mini"
)
async def main():
    # result=Runner.run_streamed(agent, input="please tell me 5 jokes")
    # async for event in result.stream_events():
    #     if event.type=="raw_response_event" and isinstance(event.data,ResponseTextDeltaEvent):
    #         print(event.data.delta, end="", flush=True)// add the even.data.delta string to the string that you want to show in the front end application
    result = Runner.run_streamed(
    joker_agent,
    input="Hello",
)
    print("=== Run starting ===")

    async for event in result.stream_events():
        # We'll ignore the raw responses event deltas
        if event.type == "raw_response_event":
            continue
        # When the agent updates, print that
        elif event.type == "agent_updated_stream_event":
            print(f"Agent updated: {event.new_agent.name}")
            continue
        # When items are generated, print them
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                print("-- Tool was called")
            elif event.item.type == "tool_call_output_item":
                print(f"-- Tool output: {event.item.output}")
            elif event.item.type == "message_output_item":
                print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
            else:
                pass  # Ignore other event types

    print("=== Run complete ===")


if __name__ == "__main__":
    asyncio.run(main())
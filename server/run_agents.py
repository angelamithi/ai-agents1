import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")

agent = Agent(
    name="Basic Agent",
    instructions="YOU ARE A HELPFUL ASSISTANT. RESPOND IN ALL CAPS",
    model="gpt-4o-mini",
)

async def main():
    result = await Runner.run(agent, "Hello! How are you?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())

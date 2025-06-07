import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner
from pydantic import BaseModel

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")

agent = Agent(
    name="Basic Agent",
    instructions="YOU ARE A HELPFUL ASSISTANT. RESPOND IN ALL CAPS",
    model="gpt-4o-mini",
)
joke_agent=Agent(
    name="Joke Agent",
    instructions="You are a joke teller. You are given a topic and you need to tell a joke about it.",
    model="gpt-4o-mini",
)
language_agent = Agent(
    name="Language Agent",
    instructions="You are a language expert. You are given a joke and you need to rewrite it in a different language.",
    model="gpt-4o-mini",
)

class Recipe(BaseModel):
    title:str
    ingredients:list[str]
    cooking_time:int
    servings:int

recipe_agent=Agent(
    name="Recipe Agent",
    instructions=("You are an agent for creating recipes. You will be given the name of a food and your job"
                  " is to output that as an actual detailed recipe. The cooking time should be in minutes."),
    model="gpt-4o-mini",
    output_type=Recipe
)

async def main():
    # result = await Runner.run(agent, "Hello! How are you?")
    # print(result.final_output)
    # topic="boogers"
    # result=await Runner.run(joke_agent, topic)
    # print(result.final_output)
    # joke_result=await Runner.run(joke_agent,topic)
    # translated_joke_result=await Runner.run(language_agent,f"Traslate this joke to Swahili:{joke_result.final_output}")
    # print(f"Original joke:\n{joke_result.final_output}\n")
    # print(f"Translated joke:\n{translated_joke_result.final_output}")
    response=await Runner.run(recipe_agent,"Italian Sausage with Spaghetti")
    print(response.final_output)

if __name__ == "__main__":
    asyncio.run(main())

import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner,function_tool,WebSearchTool
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
@function_tool
def get_weather(city:str)-> str:
    print(f"Get weather for {city}")
    return f" The weather for {city} is sunny"
@function_tool
def get_temperature(city:str)->str:
    print(f"Get temperature for {city}") 
    return f"The temperature for {city}is 70 degrees"

weather_agent=Agent(
     name="Weather Agent",
     instructions="You are the local weather agent. You are given a city and you need to tell the weather and temperature. For any unrelated queries, say I cant help with that.",
     model="gpt-4o-mini",
     tools=[get_weather,get_temperature]
 )
news_agent=Agent(
    name="News Agent",
    instructions="You are a news reporter. Your job is to find recent news articles on the internet about US politics.",
    model="gpt-4o-mini",
    tools=[WebSearchTool()]
)
news_agent2=Agent(
    name="News Agent2",
    instructions="You are a news agent that can search the web for the latest newson a given topic."+
    "Compile the information you find into a concise 1 paragraph summary.No markdown,just plain text",
    model="gpt-4o-mini",
    tools=[WebSearchTool()]
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
    # response=await Runner.run(recipe_agent,"Italian Sausage with Spaghetti")
    # print(response.final_output)
    # weather_result=await Runner.run(weather_agent,"Nairobi")
    # print(weather_result.final_output)
    # news_result=await Runner.run(news_agent,"find news")
    # print(news_result.final_output)
    while True:
        query=input("Enter your news query(or 'quit'to exit)")
        if query.lower=="quit":
            break
        result=await Runner.run(news_agent2,query)
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())

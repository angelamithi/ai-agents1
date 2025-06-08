import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner,function_tool,WebSearchTool,handoff,RunContextWrapper
from pydantic import BaseModel
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")

class Tutorial(BaseModel):
    outline:str
    tutorial:str

tutorial_generator=Agent(
    name="Tutorial Generator Agent",
    handoff_description="Used for generating a tutorial based on an outline.",
    instructions=(
        "Given a programming topic and an outline, your job is to generate code snippets for each section of the outline."
        "Format the tutorial in Markdown using a mix of text for explanation and code snippets for examples."
        "Where it makes sense, include comments in the code snippets to further explain the code."
    ),
    model="gpt-4o-mini",
    output_type=Tutorial

)


outline_builder=Agent(
    name="Outline Builder Agent",
    instructions=(
        "Given a particular programming topic, your job is to help come up with a tutorial. You will do that by crafting an outline."
        "After making the outline, hand it to the tutorial generator agent."
    ),
    model="gpt-4o-mini",
    handoffs=[tutorial_generator]
)
def on_math_handoff(ctx: RunContextWrapper[None]):
    print("Handing off to math tutor agent")

def on_history_handoff(ctx: RunContextWrapper[None]):
    print("Handing off to history tutor agent")

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
    model="gpt-4o-mini",
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide assistance with math queries. Explain your reasoning at each step and include examples",
    model="gpt-4o-mini",
)

# This agent has the capability to handoff to either the history or math tutor agent
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question." +
    "If neither agent is relevant, provide a general response.",
    handoffs=[handoff(history_tutor_agent, on_handoff=on_history_handoff), 
              handoff(math_tutor_agent, on_handoff=on_math_handoff)]
)
class ManagerEscalation(BaseModel):
    issue: str # the issue being escalated
    why: str # why can you not handle it? Used for training in the future

@function_tool
def create_ticket(issue: str):
    """"
    Create a ticket in the system for an issue to be resolved.
    """
    print(f"Creating ticket for issue: {issue}")
    return "Ticket created. ID: 12345"
    # In a real-world scenario, this would interact with a ticketing system
manager_agent = Agent(
    name="Manager",
    handoff_description="Handles escalated issues that require managerial attention",
    instructions=(
        "You handle escalated customer issues that the initial custom service agent could not resolve. "
        "You will receive the issue and the reason for escalation. If the issue cannot be immediately resolved for the "
        "customer, create a ticket in the system and inform the customer."
    ),
    tools=[create_ticket],
)
def on_manager_handoff(ctx: RunContextWrapper[None], input: ManagerEscalation):
    print("Escalating to manager agent: ", input.issue)
    print("Reason for escalation: ", input.why)

    # here we might store the escalation in a database or log it for future reference
customer_service_agent = Agent(
    name="Customer Service",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
                You assist customers with general inquiries and basic troubleshooting. +
                 If the issue cannot be resolved, escalate it to the Manager along with the reason why you cannot fix the issue yourself.""",
    handoffs=[handoff(
        agent=manager_agent,
        input_type=ManagerEscalation,
        on_handoff=on_manager_handoff,
    )]
)
async def main():
    # tutorial_response=await Runner.run(outline_builder,"Loops in Java")
    # print(tutorial_response.final_output)

    # result = await Runner.run(triage_agent, "How do I add 2 and 2?")
    # print(result.final_output)
    # result = await Runner.run(triage_agent, "How did WW2 start?")
    # print(result.final_output)
    # result = await Runner.run(customer_service_agent, "Hello how much are tickets?")
    # print(result.final_output)
    result = await Runner.run(customer_service_agent, "I want a refund,but your system wont let me process it.The website is just blank for me to process a refund?")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())

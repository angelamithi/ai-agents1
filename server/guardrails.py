

from agents import Agent, GuardrailFunctionOutput,  OutputGuardrailTripwireTriggered, output_guardrail, RunContextWrapper, Runner, TResponseInputItem, input_guardrail
from pydantic import BaseModel
import asyncio
import os
from dotenv import load_dotenv


# This should trigger the cheat detection guardrail
from agents import InputGuardrailTripwireTriggered
load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")

class HomeworkCheatDetectionOutput(BaseModel):
    attempting_cheat: bool
    explanation: str

homework_cheat_guardrail_agent = Agent(
    name="Homework Cheat Detector",
    instructions=(
        "Determine if the user's query resembles a typical homework assignment or exam question, indicating an attempt to cheat. General questions about concepts are acceptable. "
        " Cheating: 'Fill in the blank: The capital of France is ____.',"
        " 'Which of the following best describes photosynthesis? A) Cellular respiration B) Conversion of light energy C) Evaporation D) Fermentation.'"
        " Not-Cheating: 'What is the capital of France?', 'Explain photosynthesis.'"
    ),
    output_type=HomeworkCheatDetectionOutput,
    model="gpt-4o-mini"
)


@input_guardrail
async def cheat_detection_guardrail(
        ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
)->GuardrailFunctionOutput:
    detection_result = await Runner.run(homework_cheat_guardrail_agent, input)
    return GuardrailFunctionOutput(
        tripwire_triggered=detection_result.final_output.attempting_cheat,
        output_info=detection_result.final_output

    )


study_helper_agent = Agent(
    name="Study Helper Agent",
    instructions="You assist users in studying by explaining concepts or providing guidance, without directly solving homework or test questions.",
    model="gpt-4o-mini",
    input_guardrails=[cheat_detection_guardrail]
)


#Output Guardrails 
class MessageOutput(BaseModel):
    response: str

@output_guardrail
async def forbidden_words_guardrail(ctx: RunContextWrapper, agent: Agent, output: str) -> GuardrailFunctionOutput:
    print(f"Checking output for forbidden phrases: {output}")

    # Funny forbidden phrases to check
    forbidden_phrases = ["fart", "booger", "silly goose"]

    # Convert output to lowercase for case-insensitive comparison
    output_lower = output.lower()

    # Check which forbidden phrases are present in the response
    found_phrases = [phrase for phrase in forbidden_phrases if phrase in output_lower]
    trip_triggered = bool(found_phrases)

    print(f"Found forbidden phrases: {found_phrases}")

    return GuardrailFunctionOutput(
        output_info={
            "reason": "Output contains forbidden phrases.",
            "forbidden_phrases_found": found_phrases,
        },
        tripwire_triggered=trip_triggered,
    )

agent = Agent(
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    output_guardrails=[forbidden_words_guardrail],
    model="gpt-4o-mini",
)

async def main():
    #Testing input guardrails
    # try:
    #     # response = await Runner.run(study_helper_agent, "Fill in the blank: The process of converting light energy into chemical energy is called ____.")
    #     response = await Runner.run(study_helper_agent, "Wht was the main cause of american civil war?.")
    #     print("Guardrail didn't trigger")
    #     print("Response: ", response.final_output)

    # except InputGuardrailTripwireTriggered as e:
    #     print("Homework cheat guardrail triggered")
    #     print("Exception details:", str(e))

    #Testing output guardrails
    # try:
    #     await Runner.run(agent, "Say the word fart")
    #     print("Guardrail didn't trip - this is unexpected")
    # except OutputGuardrailTripwireTriggered:
    #         print("The agent said a bad word, he is fired.")
    

    try:
        await Runner.run(agent, "Hey wassup")
        print("Guardrail didn't trip yay")
    except OutputGuardrailTripwireTriggered:
        print("The agent said a bad word, he is fired.")





if __name__ == "__main__":
    asyncio.run(main())
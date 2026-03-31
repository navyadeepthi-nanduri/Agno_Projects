from agno.agent import Agent
from agno.models.google import Gemini
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

def get_agent():
    agent = Agent(
        name="Web Chat Agent",
        model=Gemini(
            id="gemini-flash-lite-latest",
            api_key=api_key
        ),
        instructions="""
You are a helpful AI assistant.
Give clear, short and helpful responses.
If coding question comes → explain simply.
"""
    )
    return agent
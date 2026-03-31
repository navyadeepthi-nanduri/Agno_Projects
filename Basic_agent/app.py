from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
from company_data import company_info
import os

# Load env
load_dotenv()

# Create agent using Gemini
agent = Agent(
    model=Gemini(id="gemini-flash-lite-latest"),  # free fast model
    instructions=f"""
You are an AI assistant for TechNova Solutions.

STRICT RULES:
- Answer only from given company information
- Do NOT use outside knowledge
- If answer not found say:
"Sorry, I don't have information about that."

Company Information:
{company_info}
""",
    markdown=True
)

print("🤖 Company AI Agent Ready (Gemini)! Type 'exit' to stop\n")

while True:
    q = input("Ask: ")

    if q.lower() == "exit":
        break

    response = agent.run(q)
    print("\nAgent:", response.content, "\n")
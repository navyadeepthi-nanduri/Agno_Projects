from agno.agent import Agent
from agno.models.google import Gemini
import os
from dotenv import load_dotenv

load_dotenv()

model = Gemini(id="gemini-flash-lite-latest")

research_agent = Agent(
    model=model,
    instructions="You are research team. Give market research."
)

marketing_agent = Agent(
    model=model,
    instructions="You are marketing team. Give marketing strategy."
)

finance_agent = Agent(
    model=model,
    instructions="You are finance team. Give budget and ROI."
)

manager_agent = Agent(
    model=model,
    instructions="""
You are project manager.
You will receive outputs from research, marketing and finance teams
and create final combined report.
"""
)

query = input("Enter project idea: ")

research_output = research_agent.run(query).content
marketing_output = marketing_agent.run(query).content
finance_output = finance_agent.run(query).content

final_prompt = f"""
Project: {query}

Research Team Output:
{research_output}

Marketing Team Output:
{marketing_output}

Finance Team Output:
{finance_output}

Create final combined business report.
"""

final = manager_agent.run(final_prompt)

print("\n===== FINAL OUTPUT =====\n")
print(final.content)
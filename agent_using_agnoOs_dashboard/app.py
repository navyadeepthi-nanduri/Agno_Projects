import os
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.groq import Groq
from agno.os import AgentOS
from agno.team import Team

# ------------------ ENV ------------------
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# ------------------ MODEL ------------------
model = Groq(
    id="llama-3.3-70b-versatile",
    api_key=api_key
)

# ------------------ AGENTS ------------------
research_agent = Agent(
    name="Research Agent",
    role="Research topics deeply",
    model=model,
    instructions="Research topic and give detailed info",
    markdown=True,
)

analyst_agent = Agent(
    name="Analyst Agent",
    role="Analyze research",
    model=model,
    instructions="Analyze and extract insights",
    markdown=True,
)

summary_agent = Agent(
    name="Summary Agent",
    role="Summarize output",
    model=model,
    instructions="Give final summary",
    markdown=True,
)

# ------------------ TEAM ------------------
team = Team(
    id="research-team",
    name="AI Research Team",
    members=[research_agent, analyst_agent, summary_agent],
    model=model,
    markdown=True,
)

# ------------------ AGENT OS ------------------
os_app = AgentOS(
    description="Multi-agent research system",
    agents=[research_agent, analyst_agent, summary_agent],
    teams=[team],
)

app = os_app.get_app()

# ------------------ RUN ------------------
if __name__ == "__main__":
    os_app.serve(app="app:app", reload=True)
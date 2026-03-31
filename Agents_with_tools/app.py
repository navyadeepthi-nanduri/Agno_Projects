from textwrap import dedent

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.duckduckgo import DuckDuckGoTools

# Create local news agent using phi3
agent = Agent(
    model=Ollama(id="llama3.1:8b"),   # local model
    instructions=dedent("""
You are an enthusiastic news reporter with a flair for storytelling!

Follow these rules:
- Give catchy headline
- Give short summary
- Provide key details
- Keep response clear and interesting
"""),
    tools=[DuckDuckGoTools()],
    markdown=True,
)

agent.print_response(
    "Tell me latest breaking news in New York Times Square",
    stream=True
)
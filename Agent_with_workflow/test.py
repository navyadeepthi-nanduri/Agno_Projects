from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv

load_dotenv()

model = Groq(id="llama-3.3-70b-versatile")

agent = Agent(
    model=model,
    instructions="You are helpful AI assistant"
)

response = agent.run("Explain RAG in simple words")
print(response.content)
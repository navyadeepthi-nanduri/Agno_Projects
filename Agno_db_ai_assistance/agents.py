from agno.agent import Agent
from agno.models.openai import OpenAIChat
import os
from dotenv import load_dotenv
import db

load_dotenv()

model = OpenAIChat(
    id="mistralai/mistral-7b-instruct",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

db_reader = Agent(
    name="DB Reader",
    model=model,
    tools=[db.fetch_users],
)

db_writer = Agent(
    name="DB Writer",
    model=model,
    tools=[db.insert_user],
)
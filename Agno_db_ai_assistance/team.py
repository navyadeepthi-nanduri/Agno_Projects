import os
from dotenv import load_dotenv
load_dotenv()

from agno.team import Team
from agno.models.openai import OpenAIChat
from agents import db_reader, db_writer

model = OpenAIChat(
    id="meta-llama/llama-3-8b-instruct",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

db_team = Team(
    name="Postgres AI Team",
    model=model,
    members=[db_reader, db_writer],
    instructions="""
If user provides name and email,
always use DB Writer to store in database.
"""
)
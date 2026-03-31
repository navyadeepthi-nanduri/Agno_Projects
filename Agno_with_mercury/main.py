import os
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools
from agno.tools.duckduckgo import DuckDuckGoTools

# Load environment variables
load_dotenv()

# Initialize the Agent
agent = Agent(
    model=OpenAIChat(
        id="mercury-2",
        api_key=os.getenv("INCEPTION_API_KEY"),
        base_url="https://api.inceptionlabs.ai/v1",
    ),
    tools=[
        YFinanceTools(),
        DuckDuckGoTools()
    ],
    markdown=True,
)

agent.print_response("""
You are a senior financial analyst.

Use yfinance to get financial data.
Use DuckDuckGo to search for recent news.
Always provide a summary of the pros and cons of an investment.

Analyze NVIDIA (NVDA) and tell me if it's a good time to buy.
""")
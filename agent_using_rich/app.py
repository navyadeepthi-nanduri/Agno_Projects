from agno.agent import Agent
from agno.models.google import Gemini
from rich.console import Console
from rich.panel import Panel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Rich console
console = Console()

# Create Agno Agent
agent = Agent(
    name="Rich Terminal Chatbot",
    model=Gemini(
        id="gemini-flash-lite-latest",
        api_key=api_key
    ),
    instructions="""
You are a helpful AI assistant.
Answer clearly and professionally.
""",
    markdown=True
)

# Welcome panel
console.print(
    Panel.fit(
        "🤖 Agno Rich Terminal Chatbot Started\nType 'exit' to quit",
        border_style="green"
    )
)

# Chat loop
while True:
    user_input = console.input("\n[bold cyan]You:[/bold cyan] ")

    if user_input.lower() == "exit":
        console.print("\n[bold red]Goodbye! Chat ended.[/bold red]")
        break

    console.print("\n[bold yellow]AI:[/bold yellow]")

    # Stream response like ChatGPT
    agent.print_response(user_input, stream=True)
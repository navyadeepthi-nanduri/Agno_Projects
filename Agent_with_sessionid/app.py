from agno.agent import Agent
from agno.models.openai import OpenAIChat
import os

# vLLM configuration
os.environ["OPENAI_BASE_URL"] = "http://vllm.dealwallet.com:8080/v1"
os.environ["OPENAI_API_KEY"] = "lIsJqsUPjkLE_BzQm48JDtKB_ubPeJd28adqWdNJgrE"

agent = Agent(
    name="CompanyAgent",
    model=OpenAIChat(
        id="Qwen/Qwen2.5-7B-Instruct"
    ),
    markdown=True
)

if __name__ == "__main__":
    print("\n🤖 Agno Agent with Session Storage (vLLM Qwen)")
    print("Type exit to stop\n")

    while True:
        user = input("You: ")

        if user.lower() == "exit":
            print("Agent: Bye 👋")
            break

        response = agent.run(
            user,
            session_id="company_session_1",  # session memory
            num_history_messages=6           # last 6 messages
        )

        print(f"Agent: {response.content}")
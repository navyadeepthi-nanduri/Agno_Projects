from agno.agent import Agent
from agno.workflow import Workflow
from agno.models.groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ---------------- MODEL ----------------
model = Groq(id="llama-3.3-70b-versatile")

# ---------------- AGENT ----------------
agent = Agent(
    name="WorkflowAgent",
    model=model,
    instructions="You are a helpful AI assistant"
)

from agno.workflow import StepOutput

# ---------------- STEP 1 ----------------
def step1(step_input):
    print("\n🟢 Step 1: Understanding query")

    user_query = step_input.input
    return user_query   # pass forward


# ---------------- STEP 2 ----------------
def step2(step_input):
    print("\n🟢 Step 2: Calling LLM")

    # get output from step1
    query = step_input.previous_step_content or step_input.input

    response = agent.run(query)
    print("LLM RAW:", response.content)

    return response.content   # pass forward


# ---------------- STEP 3 ----------------
def step3(step_input):
    print("\n🟢 Step 3: Final output")

    # get LLM output from step2
    final_answer = step_input.previous_step_content or step_input.input

    return f"\n✅ Final Answer:\n{final_answer}"
    
# ---------------- WORKFLOW ----------------
workflow = Workflow(
    name="GroqWorkflow",
    steps=[step1, step2, step3]
)

# ---------------- RUN ----------------
if __name__ == "__main__":
    while True:
        q = input("\nEnter query: ")

        if q.lower() == "exit":
            break

        result = workflow.run(q)
        print(result.content)
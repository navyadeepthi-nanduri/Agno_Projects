# =========================================================
# Resume Screening Agent with Guardrails (Agno Framework)
# =========================================================

from typing import Union
from dotenv import load_dotenv
import os

from agno.agent import Agent
from agno.models.google import Gemini
from agno.guardrails import PIIDetectionGuardrail, PromptInjectionGuardrail
from agno.guardrails.base import BaseGuardrail
from agno.exceptions import InputCheckError
from agno.run.agent import RunInput
from agno.run.team import TeamRunInput

# ---------------------------------------------------------
# Load ENV variables
# ---------------------------------------------------------
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

if not google_api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env file")

# ---------------------------------------------------------
# Custom Guardrail: Resume Length Check
# ---------------------------------------------------------
class ResumeLengthGuardrail(BaseGuardrail):
    """Blocks very short resumes"""

    def check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        content = run_input.input_content_string()

        if len(content.strip()) < 50:
            raise InputCheckError("Resume too short. Please provide full resume.")

    async def async_check(self, run_input):
        self.check(run_input)

# ---------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------
instructions = """
You are an HR Resume Screening AI Agent.

Analyze the given resume and provide:
- Key skills
- Experience level (Fresher/Junior/Mid/Senior)
- Suggested job role
- Final decision: Shortlist or Reject

Keep response professional and short.
"""

# ---------------------------------------------------------
# Create Agent with Guardrails
# ---------------------------------------------------------
resume_agent = Agent(
    name="Resume Guardrail Agent",

    # 🔥 Compatible Gemini model for your API key
    model=Gemini(
        id="gemini-flash-lite-latest",
        api_key=google_api_key
    ),

    instructions=instructions,

    pre_hooks=[
        PIIDetectionGuardrail(mask_pii=True),  # mask phone/email
        PromptInjectionGuardrail(),            # block jailbreak
        ResumeLengthGuardrail(),               # custom guardrail
    ],

    markdown=True,
)

# ---------------------------------------------------------
# Run Agent
# ---------------------------------------------------------
if __name__ == "__main__":

    print("\n🟢 Resume Screening Agent with Guardrails Started\n")

    try:
        # Read resume from file
        with open("resume.txt", "r", encoding="utf-8") as f:
            user_input = f.read()

        print("\n🔍 Analyzing resume from resume.txt...\n")
        resume_agent.print_response(user_input, stream=True)

    except InputCheckError as e:
        print(f"\n❌ BLOCKED by Guardrail: {e.message}")

    except FileNotFoundError:
        print("\n❌ resume.txt file not found. Create resume.txt in same folder.")

    except Exception as e:
        print(f"\n⚠️ Error: {str(e)}")
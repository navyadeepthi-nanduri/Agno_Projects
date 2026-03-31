from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from agno.os import AgentOS
from agents import db_reader, db_writer
from team import db_team
import re

# ---------------- AGNO OS ----------------
os_app = AgentOS(
    description="Postgres AI system",
    agents=[db_reader, db_writer],
    teams=[db_team],
)

app: FastAPI = os_app.get_app()

# ---------------- CUSTOM ROUTER ----------------
@app.post("/api/chat")
async def custom_chat(request: Request):
    data = await request.json()
    user_input = data.get("message", "")
    text = user_input.lower()

    # -------- INSERT USER --------
    if "add user" in text or "store user" in text:
        name_match = re.search(r"name\s+(\w+)", text)
        email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)

        if name_match and email_match:
            name = name_match.group(1)
            email = email_match.group(0)

            db_writer.tools[0](name=name, email=email)
            return JSONResponse({"response": f"✅ User {name} stored in database"})

        return JSONResponse({"response": "⚠️ Provide name and email clearly"})

    # -------- FETCH USERS --------
    if "show users" in text or "fetch users" in text:
        result = db_reader.tools[0]()
        return JSONResponse({"response": result})

    # -------- NORMAL CHAT --------
    result = db_team.run(user_input)
    return JSONResponse({"response": str(result)})


# ---------------- RUN ----------------
if __name__ == "__main__":
    os_app.serve(app="app:app", reload=False)
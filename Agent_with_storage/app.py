import sqlite3
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq

# ---------------- LOAD ENV ----------------
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ GROQ API KEY NOT FOUND. Check .env file")
    exit()

# ---------------- DATABASE ----------------
conn = sqlite3.connect("agent_memory.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS memory (
    role TEXT,
    message TEXT
)
""")
conn.commit()

# ---------------- AGENT ----------------
agent = Agent(
    name="PersistentMemoryAgent",
    model=Groq(
        id="llama-3.3-70b-versatile",   # best model
        api_key=api_key
    ),
    markdown=True
)

# ---------------- CHAT LOOP ----------------
print("\n🤖 Groq Persistent Memory Agent Started")
print("Type 'exit' to stop\n")

while True:
    user = input("You: ")

    if user.lower() == "exit":
        print("Agent: Bye 👋")
        break

    # store user message
    cursor.execute("INSERT INTO memory VALUES (?,?)", ("user", user))
    conn.commit()

    # get last 6 messages (avoid overload)
    cursor.execute("SELECT role, message FROM memory ORDER BY rowid DESC LIMIT 6")
    rows = cursor.fetchall()

    history = ""
    for r in reversed(rows):
        history += f"{r[0]}: {r[1]}\n"

    # send to agent
    response = agent.run(history)

    print("Agent:", response.content)

    # store agent reply
    cursor.execute("INSERT INTO memory VALUES (?,?)", ("assistant", response.content))
    conn.commit()   
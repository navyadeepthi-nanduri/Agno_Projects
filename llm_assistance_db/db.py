import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"),
        database=os.getenv("PG_DB"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD")
    )

# INSERT USER
def insert_user(name, email):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO user2 (name,email) VALUES (%s,%s)",
        (name, email)
    )

    conn.commit()
    cur.close()
    conn.close()

    return f"{name} stored successfully"

# FETCH USERS
def get_users():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name,email FROM user2")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows
import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="agno_db1",
        user="postgres",
        password="Pgadmin@12",
        port="5432"
    )

def insert_user(name, email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO user1(name,email) VALUES (%s,%s)",
        (name,email)
    )
    conn.commit()
    cur.close()
    conn.close()
    return f"{name} stored successfully"

def fetch_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user1")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return "No users found"

    return rows
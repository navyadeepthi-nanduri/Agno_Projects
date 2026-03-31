def insert_user(name: str, email: str):
    print("INSERTING:", name, email)
    """
    Insert a new user into the users table.

    Args:
        name (str): User's name
        email (str): User's email

    Returns:
        str: Confirmation message
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        (name, email)
    )
    conn.commit()
    cur.close()
    conn.close()
    return f"User {name} inserted successfully"
def fetch_users():
    print("FETCHING USERS FROM DB")  # debug print

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users;")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        return "No users found in database."

    result = []
    for row in rows:
        result.append(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}")

    return "\n".join(result)
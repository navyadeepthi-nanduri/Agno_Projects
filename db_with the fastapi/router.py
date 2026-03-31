import re
import db


def handle_query(user_input: str):

    text = user_input.lower()

    # -------- INSERT USER --------
    if "add user" in text:
        name_match = re.search(r"name\s+(\w+)", text)
        email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)

        if name_match and email_match:
            name = name_match.group(1)
            email = email_match.group(0)
            return db.insert_user(name,email)

        return "Provide name and email"

    # -------- FETCH USERS --------
    if "show users" in text or "get users" in text:
        return db.fetch_users()

    
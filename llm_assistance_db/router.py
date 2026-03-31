import db
from llm import ask_ai

def handle_query(message: str):

    msg = message.lower()

    # add user
    if "add user" in msg:
        try:
            words = msg.split()
            name = words[words.index("name")+1]
            email = words[words.index("email")+1]
            return db.insert_user(name,email)
        except(ValueError, IndexError):
            return "Format: add user name <name> email <email>"

    # show users
    elif "show users" in msg:
        return db.fetch_users()

    # AI question
    else:
        return ask_ai(message)
import streamlit as st
from agent_config import get_agent

# Load agent
agent = get_agent()

# UI title
st.set_page_config(page_title="Agno AI Chatbot", page_icon="🤖")
st.title("🤖 Agno Web Chatbot")
st.write("Ask anything...")

# Chat history session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input
user_input = st.chat_input("Type your message...")

if user_input:
    # show user msg
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # agent response
    with st.spinner("Thinking..."):
        response = agent.run(user_input)
        reply = response.content

    # show bot msg
    st.chat_message("assistant").write(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
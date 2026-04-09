import os
import requests
import streamlit as st

# =========================
# CONFIG
# =========================
BACKEND_CHAT_URL = os.getenv("BACKEND_CHAT_URL", "http://127.0.0.1:8000/chat")

st.set_page_config(
    page_title="Gemma Multimodal Chatbot",
    page_icon="🤖",
    layout="wide",
)

# =========================
# CUSTOM CSS (Classy UI)
# =========================
st.markdown(
    """
    <style>
    .main {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    .app-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .app-subtitle {
        color: #9aa0a6;
        margin-bottom: 1.5rem;
        font-size: 1rem;
    }

    .stChatMessage {
        border-radius: 14px;
    }

    .meta-box {
        background-color: #111827;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 12px;
        color: #e5e7eb;
        font-size: 0.95rem;
        margin-top: 10px;
    }

    .composer-box {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 14px;
        margin-top: 10px;
    }

    .small-note {
        color: #94a3b8;
        font-size: 0.9rem;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        height: 42px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# SESSION STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_meta" not in st.session_state:
    st.session_state.last_meta = ""

# =========================
# HEADER
# =========================
st.markdown('<div class="app-title">🤖 Gemma Multimodal Chatbot</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Supports text, image, audio, and mixed multimodal inputs using FastAPI + OpenRouter + Groq.</div>',
    unsafe_allow_html=True,
)

# =========================
# CHAT HISTORY DISPLAY
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================
# INPUT AREA
# =========================
st.markdown('<div class="composer-box">', unsafe_allow_html=True)

user_text = st.chat_input("Ask anything... or upload image/audio below and click Send")

col1, col2, col3 = st.columns([1, 1, 0.7])

with col1:
    uploaded_image = st.file_uploader(
        "📷 Upload Image (optional)",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=False,
        key="image_uploader",
    )

with col2:
    uploaded_audio = st.file_uploader(
        "🎤 Upload Audio (optional)",
        type=["wav", "mp3", "m4a", "webm"],
        accept_multiple_files=False,
        key="audio_uploader",
    )

with col3:
    send_clicked = st.button("🚀 Send", use_container_width=True)
    clear_clicked = st.button("🗑️ Clear Chat", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="small-note">Tip: You can use text only, image only, audio only, or any combination of them.</div>',
    unsafe_allow_html=True,
)

# =========================
# CLEAR CHAT
# =========================
if clear_clicked:
    st.session_state.messages = []
    st.session_state.last_meta = ""
    st.rerun()

# =========================
# SEND LOGIC
# =========================
def call_backend(text_input, image_file, audio_file):
    files = {}
    data = {}

    if text_input and text_input.strip():
        data["text_input"] = text_input.strip()

    if image_file is not None:
        files["image"] = (image_file.name, image_file.getvalue(), image_file.type or "application/octet-stream")

    if audio_file is not None:
        files["audio"] = (audio_file.name, audio_file.getvalue(), audio_file.type or "application/octet-stream")

    if not data and not files:
        return {
            "ok": False,
            "error": "Please provide text, image, audio, or a combination."
        }

    try:
        response = requests.post(
            BACKEND_CHAT_URL,
            data=data,
            files=files,
            timeout=180,
        )

        if response.status_code != 200:
            try:
                err_json = response.json()
                error_detail = err_json.get("detail", str(err_json))
            except Exception:
                error_detail = response.text

            return {
                "ok": False,
                "error": f"Backend error ({response.status_code}): {error_detail}"
            }

        result = response.json()
        return {
            "ok": True,
            "data": result
        }

    except requests.exceptions.ConnectionError:
        return {
            "ok": False,
            "error": "Could not connect to backend. Make sure FastAPI is running on http://127.0.0.1:8000"
        }
    except requests.exceptions.Timeout:
        return {
            "ok": False,
            "error": "Request timed out while waiting for backend response."
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"Unexpected frontend error: {str(e)}"
        }

# Trigger send if:
# - user pressed Send button
# OR
# - user pressed Enter in chat_input (text-only flow)
should_send = send_clicked or (user_text is not None and user_text.strip())

if should_send:
    # Build user preview message for chat window
    preview_parts = []

    if user_text and user_text.strip():
        preview_parts.append(f"**Text:** {user_text.strip()}")

    if uploaded_image is not None:
        preview_parts.append(f"**Image:** {uploaded_image.name}")

    if uploaded_audio is not None:
        preview_parts.append(f"**Audio:** {uploaded_audio.name}")

    if not preview_parts:
        st.warning("Please provide text, image, audio, or a combination.")
    else:
        user_preview = "\n\n".join(preview_parts)

        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_preview
        })

        # Re-render user message immediately
        with st.chat_message("user"):
            st.markdown(user_preview)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                backend_result = call_backend(user_text, uploaded_image, uploaded_audio)

                if not backend_result["ok"]:
                    assistant_reply = f"❌ {backend_result['error']}"
                    st.error(assistant_reply)
                    st.session_state.last_meta = "Request failed."
                else:
                    result = backend_result["data"]
                    assistant_reply = result.get("model_response", "No response received.")
                    input_mode = result.get("input_mode", "unknown")
                    transcribed_audio = result.get("transcribed_audio")
                    errors = result.get("errors", [])

                    # Build metadata
                    meta_lines = [f"**Input Mode:** {input_mode}"]

                    if transcribed_audio:
                        meta_lines.append(f"**Transcribed Audio:** {transcribed_audio}")

                    if errors:
                        meta_lines.append(f"**Warnings:** {' | '.join(errors)}")

                    st.session_state.last_meta = "\n\n".join(meta_lines)

                    st.markdown(assistant_reply)

        # Save assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_reply
        })

        # Rerun so the UI refreshes cleanly after send
        st.rerun()

# =========================
# METADATA PANEL
# =========================
if st.session_state.last_meta:
    st.markdown("### ℹ️ Last Request Details")
    st.markdown(
        f'<div class="meta-box">{st.session_state.last_meta.replace(chr(10), "<br>")}</div>',
        unsafe_allow_html=True,
    )
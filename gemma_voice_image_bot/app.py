import os
import gradio as gr
from dotenv import load_dotenv

from utils.image_utils import load_image_base64
from utils.stt_utils import transcribe_audio
from utils.gemma_client import ask_gemma_with_image

# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------
load_dotenv()
API_KEY = os.getenv("NVIDIA_API_KEY")

if not API_KEY:
    raise ValueError("NVIDIA_API_KEY not found in .env file")

# --------------------------------------------------
# 2. Load fixed image once
# --------------------------------------------------
IMAGE_PATH = "assets/image.jpg"   # <-- make sure this matches your actual file
image_b64, mime_type = load_image_base64(IMAGE_PATH)

# --------------------------------------------------
# 3. Main unified chatbot function
# --------------------------------------------------
def unified_chatbot(input_mode, audio_input, text_input, history):
    """
    One single bot:
    - If Text mode -> use text input
    - If Voice mode -> transcribe audio
    - In both cases -> same fixed image + same Gemma model
    """

    if history is None:
        history = []

    # Decide user query based on mode
    if input_mode == "Text":
        if not text_input or not text_input.strip():
            history.append({
                "role": "assistant",
                "content": "⚠️ Please type a question."
            })
            return history, ""

        user_query = text_input.strip()

    elif input_mode == "Voice":
        if audio_input is None:
            history.append({
                "role": "assistant",
                "content": "⚠️ Please record or upload audio."
            })
            return history, ""

        user_query = transcribe_audio(audio_input)

        # If STT failed
        if (
            user_query.startswith("Sorry")
            or user_query.startswith("Speech recognition error")
            or user_query == "No audio provided."
        ):
            history.append({
                "role": "assistant",
                "content": f"⚠️ Voice input could not be processed.\n\nDetails: {user_query}"
            })
            return history, ""

    else:
        history.append({
            "role": "assistant",
            "content": "⚠️ Invalid input mode selected."
        })
        return history, ""

    # Add user message to chat history
    if input_mode == "Voice":
        history.append({
            "role": "user",
            "content": f"🎤 {user_query}"
        })
    else:
        history.append({
            "role": "user",
            "content": user_query
        })

    # Ask Gemma with fixed image
    bot_reply = ask_gemma_with_image(
        user_text=user_query,
        api_key=API_KEY,
        image_b64=image_b64,
        mime_type=mime_type
    )

    # Add assistant reply to chat history
    history.append({
        "role": "assistant",
        "content": bot_reply
    })

    # Clear text input after submit
    return history, ""

# --------------------------------------------------
# 4. Build single unified Gradio UI
# --------------------------------------------------
with gr.Blocks(title="Gemma 4 Voice + Image Unified Bot") as demo:
    gr.Markdown("# 🎙️🖼️ Gemma 4 Unified Multimodal Chatbot")
    gr.Markdown(
        "Single bot with selectable input mode (Text or Voice). "
        "The same fixed image is used for every query."
    )

    chatbot = gr.Chatbot(
        label="Chat History",
        height=400,
          # IMPORTANT FIX
    )

    input_mode = gr.Dropdown(
        choices=["Text", "Voice"],
        value="Text",
        label="Select Input Mode"
    )

    audio_input = gr.Audio(
        sources=["microphone", "upload"],
        type="filepath",
        label="🎤 Voice Input (for Voice mode)"
    )

    text_input = gr.Textbox(
        label="⌨️ Text Input (for Text mode)",
        placeholder="Ask something about the fixed image..."
    )

    with gr.Row():
        submit_btn = gr.Button("Send", variant="primary")
        clear_btn = gr.Button("Clear Chat")

    state = gr.State([])

    submit_btn.click(
        fn=unified_chatbot,
        inputs=[input_mode, audio_input, text_input, state],
        outputs=[chatbot, text_input]
    ).then(
        fn=lambda history: history,
        inputs=[chatbot],
        outputs=[state]
    )

    clear_btn.click(
        fn=lambda: ([], "", []),
        inputs=[],
        outputs=[chatbot, text_input, state]
    )

demo.launch()
import requests

def ask_gemma_with_image(user_text, api_key, image_b64, mime_type):
    invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    payload = {
        "model": "google/gemma-4-31b-it",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful multimodal assistant. "
                    "Answer only based on the provided fixed image and the user's question. "
                    "Be concise and direct."
                )
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_b64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300,   # reduced from 1024
        "temperature": 0.3,  # lower for faster/stabler response
        "top_p": 0.9,
        "stream": False
        # Removed chat_template_kwargs to avoid extra reasoning delay
    }

    try:
        response = requests.post(
            invoke_url,
            headers=headers,
            json=payload,
            timeout=(20, 180)   # connect timeout 20s, read timeout 180s
        )
        data = response.json()
    except requests.exceptions.Timeout:
        return (
            "⚠️ NVIDIA API request timed out.\n\n"
            "Possible reasons:\n"
            "- Large multimodal model response is taking too long\n"
            "- Network latency / office firewall / VPN\n"
            "- NVIDIA hosted endpoint is slow right now\n\n"
            "Recommended fix:\n"
            "- Try a shorter question\n"
            "- Retry once\n"
            "- Test on mobile hotspot\n"
        )
    except Exception as e:
        return (
            "⚠️ Unable to reach NVIDIA API.\n\n"
            f"Technical details: {str(e)}"
        )

    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        return f"⚠️ API Error / Unexpected response:\n{data}"
const chatMessages = document.getElementById("chatMessages");
const emptyState = document.getElementById("emptyState");

const messageInput = document.getElementById("messageInput");
const imageInput = document.getElementById("imageInput");
const audioInput = document.getElementById("audioInput");

const sendBtn = document.getElementById("sendBtn");
const clearChatBtn = document.getElementById("clearChatBtn");

const attachmentPreview = document.getElementById("attachmentPreview");
const imagePreviewRow = document.getElementById("imagePreviewRow");
const audioPreviewRow = document.getElementById("audioPreviewRow");

const imageFileName = document.getElementById("imageFileName");
const audioFileName = document.getElementById("audioFileName");

const removeImageBtn = document.getElementById("removeImageBtn");
const removeAudioBtn = document.getElementById("removeAudioBtn");

const detailsPanel = document.getElementById("detailsPanel");
const detailsContent = document.getElementById("detailsContent");

const CHAT_API_URL = "/chat";

let isSending = false;

// ----------------------------
// Utility functions
// ----------------------------
function hideEmptyState() {
  if (emptyState) {
    emptyState.classList.add("hidden");
  }
}

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.innerText = text;
  return div.innerHTML;
}

function nl2br(text) {
  return escapeHtml(text).replace(/\n/g, "<br>");
}

// ----------------------------
// Message rendering
// ----------------------------
function addMessage(role, content, isLoading = false) {
  hideEmptyState();

  const row = document.createElement("div");
  row.className = `message-row ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";

  if (isLoading) {
    bubble.classList.add("loading-bubble");
  }

  const meta = document.createElement("div");
  meta.className = "message-meta";
  meta.textContent = role === "user" ? "You" : "Gemma";

  const body = document.createElement("div");
  body.className = "message-body";
  body.innerHTML = nl2br(content);

  bubble.appendChild(meta);
  bubble.appendChild(body);
  row.appendChild(bubble);

  chatMessages.appendChild(row);
  scrollToBottom();

  return { row, bubble, body };
}

function updateLoadingMessage(messageObj, newContent) {
  if (!messageObj || !messageObj.body || !messageObj.bubble) return;
  messageObj.body.innerHTML = nl2br(newContent);
  messageObj.bubble.classList.remove("loading-bubble");
  scrollToBottom();
}

// ----------------------------
// Attachment preview
// ----------------------------
function updateAttachmentPreview() {
  const hasImage = imageInput.files && imageInput.files.length > 0;
  const hasAudio = audioInput.files && audioInput.files.length > 0;

  if (!hasImage && !hasAudio) {
    attachmentPreview.classList.add("hidden");
    imagePreviewRow.classList.add("hidden");
    audioPreviewRow.classList.add("hidden");
    return;
  }

  attachmentPreview.classList.remove("hidden");

  if (hasImage) {
    imagePreviewRow.classList.remove("hidden");
    imageFileName.textContent = imageInput.files[0].name;
  } else {
    imagePreviewRow.classList.add("hidden");
  }

  if (hasAudio) {
    audioPreviewRow.classList.remove("hidden");
    audioFileName.textContent = audioInput.files[0].name;
  } else {
    audioPreviewRow.classList.add("hidden");
  }
}

function clearImageFile() {
  imageInput.value = "";
  updateAttachmentPreview();
}

function clearAudioFile() {
  audioInput.value = "";
  updateAttachmentPreview();
}

// ----------------------------
// Details panel
// ----------------------------
function updateDetails(result) {
  const inputMode = result.input_mode || "unknown";
  const transcribedAudio = result.transcribed_audio;
  const errors = result.errors || [];

  let html = `<p><strong>Input Mode:</strong> ${escapeHtml(inputMode)}</p>`;

  if (transcribedAudio) {
    html += `<p><strong>Transcribed Audio:</strong> ${escapeHtml(transcribedAudio)}</p>`;
  }

  if (errors.length > 0) {
    html += `<p><strong>Warnings:</strong> ${escapeHtml(errors.join(" | "))}</p>`;
  }

  detailsContent.innerHTML = html;
  detailsPanel.classList.remove("hidden");
}

// ----------------------------
// Send logic
// ----------------------------
async function sendMessage() {
  if (isSending) return;

  const text = messageInput.value.trim();
  const imageFile = imageInput.files[0] || null;
  const audioFile = audioInput.files[0] || null;

  if (!text && !imageFile && !audioFile) {
    alert("Please provide text, image, audio, or any combination.");
    return;
  }

  isSending = true;
  sendBtn.disabled = true;
  sendBtn.textContent = "Sending...";

  // Build user preview
  const previewParts = [];

  if (text) {
    previewParts.push(`Text:\n${text}`);
  }

  if (imageFile) {
    previewParts.push(`Image: ${imageFile.name}`);
  }

  if (audioFile) {
    previewParts.push(`Audio: ${audioFile.name}`);
  }

  addMessage("user", previewParts.join("\n\n"));

  const loadingMsg = addMessage("bot", "Thinking...", true);

  const formData = new FormData();

  if (text) {
    formData.append("text_input", text);
  }

  if (imageFile) {
    formData.append("image", imageFile);
  }

  if (audioFile) {
    formData.append("audio", audioFile);
  }

  try {
    const response = await fetch(CHAT_API_URL, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      let errorText = `Backend error (${response.status})`;
      try {
        const errorJson = await response.json();
        if (errorJson.detail) {
          errorText += `: ${JSON.stringify(errorJson.detail)}`;
        }
      } catch (e) {
        // ignore parse errors
      }

      updateLoadingMessage(loadingMsg, `❌ ${errorText}`);
      return;
    }

    const result = await response.json();

    const botReply = result.model_response || "No response received.";
    updateLoadingMessage(loadingMsg, botReply);
    updateDetails(result);

    // Clear inputs after successful send
    messageInput.value = "";
    clearImageFile();
    clearAudioFile();

  } catch (error) {
    updateLoadingMessage(
      loadingMsg,
      `❌ Could not connect to backend. Make sure FastAPI is running on http://127.0.0.1:8000`
    );
  } finally {
    isSending = false;
    sendBtn.disabled = false;
    sendBtn.textContent = "🚀 Send";
    messageInput.focus();
  }
}

// ----------------------------
// Event listeners
// ----------------------------
sendBtn.addEventListener("click", sendMessage);

clearChatBtn.addEventListener("click", () => {
  chatMessages.innerHTML = "";
  if (emptyState) {
    emptyState.classList.remove("hidden");
    chatMessages.appendChild(emptyState);
  }
  detailsPanel.classList.add("hidden");
  detailsContent.innerHTML = "";
  messageInput.value = "";
  clearImageFile();
  clearAudioFile();
});

imageInput.addEventListener("change", updateAttachmentPreview);
audioInput.addEventListener("change", updateAttachmentPreview);

removeImageBtn.addEventListener("click", clearImageFile);
removeAudioBtn.addEventListener("click", clearAudioFile);

// Ctrl+Enter or Cmd+Enter to send
messageInput.addEventListener("keydown", (event) => {
  const isCtrlOrCmd = event.ctrlKey || event.metaKey;

  if (isCtrlOrCmd && event.key === "Enter") {
    event.preventDefault();
    sendMessage();
  }
});

// Auto focus on load
window.addEventListener("load", () => {
  messageInput.focus();
});
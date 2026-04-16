const chatMessages = document.getElementById("chatMessages");
const emptyState = document.getElementById("emptyState");

const messageInput = document.getElementById("messageInput");
const imageInput = document.getElementById("imageInput");
const audioInput = document.getElementById("audioInput");

const sendBtn = document.getElementById("sendBtn");
const clearChatBtn = document.getElementById("clearChatBtn");
const newChatBtn = document.getElementById("newChatBtn");

const attachmentPreview = document.getElementById("attachmentPreview");
const imagePreviewRow = document.getElementById("imagePreviewRow");
const audioPreviewRow = document.getElementById("audioPreviewRow");

const imageFileName = document.getElementById("imageFileName");
const audioFileName = document.getElementById("audioFileName");

const removeImageBtn = document.getElementById("removeImageBtn");
const removeAudioBtn = document.getElementById("removeAudioBtn");

const historyList = document.getElementById("historyList");

const CHAT_API_URL = "/chat";
const STORAGE_KEY = "gemma_chat_sessions";

let isSending = false;
let currentChatId = null;
let chatSessions = [];

// ----------------------------
// Utility
// ----------------------------
function escapeHtml(text) {
  const div = document.createElement("div");
  div.innerText = text;
  return div.innerHTML;
}

function nl2br(text) {
  return escapeHtml(text).replace(/\n/g, "<br>");
}

function generateId() {
  return "chat_" + Date.now() + "_" + Math.random().toString(36).slice(2, 8);
}

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ----------------------------
// Storage
// ----------------------------
function saveSessions() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(chatSessions));
}

function loadSessions() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    chatSessions = [];
    return;
  }

  try {
    chatSessions = JSON.parse(raw);
  } catch (e) {
    chatSessions = [];
  }
}

function getCurrentSession() {
  return chatSessions.find((s) => s.id === currentChatId);
}

// ----------------------------
// History Sidebar
// ----------------------------
function renderHistory() {
  historyList.innerHTML = "";

  if (chatSessions.length === 0) {
    const empty = document.createElement("div");
    empty.className = "history-empty";
    empty.textContent = "No chats yet";
    historyList.appendChild(empty);
    return;
  }

  [...chatSessions]
    .sort((a, b) => b.updatedAt - a.updatedAt)
    .forEach((session) => {
      const btn = document.createElement("button");
      btn.className = "history-item";

      if (session.id === currentChatId) {
        btn.classList.add("active");
      }

      btn.textContent = session.title || "New Chat";
      btn.addEventListener("click", () => {
        currentChatId = session.id;
        renderHistory();
        renderCurrentChat();
      });

      historyList.appendChild(btn);
    });
}

// ----------------------------
// Chat Rendering
// ----------------------------
function createMessageElement(role, content, isLoading = false) {
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

  return { row, bubble, body };
}

function appendMessageToUI(role, content, isLoading = false) {
  if (emptyState && emptyState.parentNode === chatMessages) {
    emptyState.remove();
  }

  const messageObj = createMessageElement(role, content, isLoading);
  chatMessages.appendChild(messageObj.row);
  scrollToBottom();
  return messageObj;
}

function renderCurrentChat() {
  chatMessages.innerHTML = "";

  const session = getCurrentSession();

  if (!session || session.messages.length === 0) {
    if (emptyState) {
      emptyState.classList.remove("hidden");
      chatMessages.appendChild(emptyState);
    }
    return;
  }

  session.messages.forEach((msg) => {
    appendMessageToUI(msg.role, msg.content, false);
  });
}

function addMessageToSession(role, content) {
  const session = getCurrentSession();
  if (!session) return;

  session.messages.push({ role, content });
  session.updatedAt = Date.now();

  if ((!session.title || session.title === "New Chat") && role === "user") {
    session.title = content.split("\n")[0].slice(0, 30) || "New Chat";
  }

  saveSessions();
  renderHistory();
}

// ----------------------------
// Attachment Preview
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
// Session Management
// ----------------------------
function createNewChat() {
  const newSession = {
    id: generateId(),
    title: "New Chat",
    messages: [],
    updatedAt: Date.now(),
  };

  chatSessions.push(newSession);
  currentChatId = newSession.id;

  saveSessions();
  renderHistory();
  renderCurrentChat();

  messageInput.value = "";
  clearImageFile();
  clearAudioFile();
  messageInput.focus();
}

function clearCurrentChat() {
  const session = getCurrentSession();
  if (!session) return;

  session.messages = [];
  session.title = "New Chat";
  session.updatedAt = Date.now();

  saveSessions();
  renderHistory();
  renderCurrentChat();
}

// ----------------------------
// Send
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

  if (!getCurrentSession()) {
    createNewChat();
  }

  isSending = true;
  sendBtn.disabled = true;
  sendBtn.textContent = "Sending...";

  const previewParts = [];
  if (text) previewParts.push(`Text:\n${text}`);
  if (imageFile) previewParts.push(`Image: ${imageFile.name}`);
  if (audioFile) previewParts.push(`Audio: ${audioFile.name}`);

  const userContent = previewParts.join("\n\n");

  appendMessageToUI("user", userContent);
  addMessageToSession("user", userContent);

  const loadingMsg = appendMessageToUI("bot", "Thinking...", true);

  const formData = new FormData();
  if (text) formData.append("text_input", text);
  if (imageFile) formData.append("image", imageFile);
  if (audioFile) formData.append("audio", audioFile);

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
        // ignore JSON parse errors
      }

      loadingMsg.body.innerHTML = nl2br(`❌ ${errorText}`);
      loadingMsg.bubble.classList.remove("loading-bubble");
      addMessageToSession("bot", `❌ ${errorText}`);
      return;
    }

    const result = await response.json();
    const botReply = result.model_response || "No response received.";

    loadingMsg.body.innerHTML = nl2br(botReply);
    loadingMsg.bubble.classList.remove("loading-bubble");

    addMessageToSession("bot", botReply);

    messageInput.value = "";
    clearImageFile();
    clearAudioFile();

  } catch (error) {
    const errMsg = "❌ Could not connect to backend. Make sure FastAPI is running.";
    loadingMsg.body.innerHTML = nl2br(errMsg);
    loadingMsg.bubble.classList.remove("loading-bubble");
    addMessageToSession("bot", errMsg);
  } finally {
    isSending = false;
    sendBtn.disabled = false;
    sendBtn.textContent = "🚀 Send";
    messageInput.focus();
    scrollToBottom();
  }
}

// ----------------------------
// Events
// ----------------------------
sendBtn.addEventListener("click", sendMessage);
newChatBtn.addEventListener("click", createNewChat);
clearChatBtn.addEventListener("click", clearCurrentChat);

imageInput.addEventListener("change", updateAttachmentPreview);
audioInput.addEventListener("change", updateAttachmentPreview);

removeImageBtn.addEventListener("click", clearImageFile);
removeAudioBtn.addEventListener("click", clearAudioFile);

messageInput.addEventListener("keydown", (event) => {
  const isCtrlOrCmd = event.ctrlKey || event.metaKey;

  if (isCtrlOrCmd && event.key === "Enter") {
    event.preventDefault();
    sendMessage();
  }
});

// ----------------------------
// Init
// ----------------------------
window.addEventListener("load", () => {
  loadSessions();

  if (chatSessions.length === 0) {
    createNewChat();
  } else {
    chatSessions.sort((a, b) => b.updatedAt - a.updatedAt);
    currentChatId = chatSessions[0].id;
    renderHistory();
    renderCurrentChat();
  }

  messageInput.focus();
});
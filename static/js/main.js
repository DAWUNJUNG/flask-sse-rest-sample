const form = document.getElementById("message-form");
const messageInput = document.getElementById("message-input");
const eventsList = document.getElementById("events");
const feedback = document.getElementById("form-feedback");

const appendEvent = (text, type = "message") => {
  const li = document.createElement("li");
  li.dataset.type = type;
  li.textContent = `${new Date().toLocaleTimeString()} — ${text}`;
  eventsList.prepend(li);
};

const handleError = (error) => {
  feedback.textContent = error;
  feedback.classList.add("error");
  setTimeout(() => feedback.classList.remove("error"), 3000);
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) {
    handleError("Please provide a message.");
    return;
  }

  ensureStreamConnection();

  try {
    const response = await fetch("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Request failed");
    }

    const { data } = await response.json();
    appendEvent(`Message accepted: ${data.message}`, "api");
    form.reset();
  } catch (err) {
    handleError(err.message);
    disconnectStream("Stream cancelled because the request failed.", "error");
  }
});

const streamStatus = document.getElementById("stream-status");
let streamSource = null;

const setStreamStatus = (text, state = "idle") => {
  if (!streamStatus) return;
  streamStatus.textContent = text;
  streamStatus.dataset.state = state;
};

const disconnectStream = (text = "Stream idle", state = "idle") => {
  if (streamSource) {
    streamSource.close();
    streamSource = null;
  }

  setStreamStatus(text, state);
};

const handleMessageEvent = (event) => {
  try {
    const payload = JSON.parse(event.data);
    const details = payload.data || {};
    const parts = [];

    if (details.message) {
      parts.push(details.message);
    }

    if (details.sequence && details.total) {
      parts.push(`(${details.sequence}/${details.total})`);
    }

    const text = parts.join(" ").trim() || JSON.stringify(details);
    appendEvent(text, "sse");
  } catch (err) {
    appendEvent(event.data, "sse");
  }
};

const handleCloseEvent = (event) => {
  let notice = "Stream completed.";
  try {
    const payload = JSON.parse(event.data);
    if (payload?.data?.message) {
      notice = `Stream completed for "${payload.data.message}".`;
    }
  } catch (_) {
    // Ignore JSON parse errors for close events.
  }

  appendEvent(notice, "status");
  disconnectStream("Stream completed.", "idle");
};

const connectStream = () => {
  if (streamSource) {
    streamSource.close();
    streamSource = null;
  }

  streamSource = new EventSource("/stream");
  setStreamStatus("Connecting to stream...", "pending");

  streamSource.addEventListener("open", () => setStreamStatus("Connected. Waiting for data...", "connected"));
  streamSource.addEventListener("keepalive", () => setStreamStatus("Awaiting message burst...", "connected"));
  streamSource.addEventListener("message", handleMessageEvent);
  streamSource.addEventListener("close", handleCloseEvent);
  streamSource.onerror = () => {
    appendEvent("Stream error or server closed connection.", "status");
    disconnectStream("Stream closed due to error.", "error");
  };
};

function ensureStreamConnection() {
  connectStream();
  appendEvent("Stream connected. Waiting for events...", "status");
}

appendEvent("Submit a message to trigger the SSE stream.", "status");

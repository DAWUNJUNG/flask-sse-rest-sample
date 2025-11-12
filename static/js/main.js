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
  }
});

const source = new EventSource("/stream");

source.addEventListener("message", (event) => {
  try {
    const payload = JSON.parse(event.data);
    appendEvent(payload.data.message || JSON.stringify(payload.data));
  } catch (err) {
    appendEvent(event.data);
  }
});

source.addEventListener("keepalive", () => {
  feedback.textContent = "Connected to stream";
  feedback.classList.remove("error");
});

source.onerror = () => {
  handleError("Connection to stream lost. Retrying...");
};

appendEvent("Connecting to server...", "status");

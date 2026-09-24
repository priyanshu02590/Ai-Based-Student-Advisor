const API_BASE = "";
let currentUser = null;

async function initChat() {
    const meResponse = await fetch(`${API_BASE}/me`, { credentials: "include" });
    const meData = await meResponse.json();

    if (meData.error) {
        window.location.href = "login.html";
        return;
    }

    currentUser = meData;
}

async function sendMessage() {
    if (!currentUser) return;

    const input = document.getElementById("chat-input");
    const message = input.value.trim();
    const chatWindow = document.getElementById("chat-window");

    if (!message) return;

    chatWindow.innerHTML += `<p class="user-msg"><strong>You:</strong> ${message}</p>`;
    input.value = "";
    chatWindow.innerHTML += `<p class="bot-msg" id="loading-msg"><strong>Advisor:</strong> Typing...</p>`;
    chatWindow.scrollTop = chatWindow.scrollHeight;

    try {
        const response = await fetch(`${API_BASE}/chat/${currentUser.id}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ message: message })
        });
        const data = await response.json();

        document.getElementById("loading-msg").remove();

        if (data.error) {
            chatWindow.innerHTML += `<p class="bot-msg">Error: ${data.error}</p>`;
        } else {
            chatWindow.innerHTML += `<div class="bot-msg"><strong>Advisor:</strong> ${marked.parse(data.reply)}</div>`;
        }
        chatWindow.scrollTop = chatWindow.scrollHeight;
    } catch (err) {
        document.getElementById("loading-msg").remove();
        chatWindow.innerHTML += `<p class="bot-msg">Something went wrong: ${err}</p>`;
    }
}

initChat();
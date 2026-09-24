const API_BASE = "";
const USER_ID = 1; // abhi hardcoded, baad mein login system se aayega

// ---- GitHub Digital Presence ----
async function fetchGithubScore() {
    const username = document.getElementById("github-username").value;
    const resultDiv = document.getElementById("github-result");

    if (!username) {
        resultDiv.innerHTML = "<p>Please enter a GitHub username.</p>";
        return;
    }

    resultDiv.innerHTML = "<p>Loading...</p>";

    try {
        const response = await fetch(`${API_BASE}/digital-presence/${username}`);
        const data = await response.json();

        if (data.error) {
            resultDiv.innerHTML = `<p>Error: ${data.error}</p>`;
            return;
        }

        resultDiv.innerHTML = `
            <div class="result-card">
                <img src="${data.avatar_url}" alt="avatar" width="60">
                <p><strong>${data.name || data.username}</strong></p>
                <p>Digital Presence Score: <strong>${data.digital_presence_score}/100</strong></p>
                <p>Public Repos: ${data.public_repos}</p>
                <p>Followers: ${data.followers}</p>
                <p>Avg Contributions/Year: ${data.average_contributions_per_year}</p>
            </div>
        `;
    } catch (err) {
        resultDiv.innerHTML = `<p>Something went wrong: ${err}</p>`;
    }
}

// ---- Weekly Wellness Insight ----
async function fetchWeeklyInsight() {
    const resultDiv = document.getElementById("insight-result");
    resultDiv.innerHTML = "<p>Loading...</p>";

    try {
        const response = await fetch(`${API_BASE}/habits/${USER_ID}/weekly-insight`);
        const data = await response.json();

        if (data.error) {
            resultDiv.innerHTML = `<p>Error: ${data.error}</p>`;
            return;
        }

        const flagsList = data.wellness_flags.map(f => `<li>${f}</li>`).join("");
        const moodList = Object.entries(data.mood_breakdown)
            .map(([mood, count]) => `<li>${mood}: ${count} day(s)</li>`)
            .join("");

        resultDiv.innerHTML = `
            <div class="result-card">
                <p>Average Sleep: <strong>${data.average_sleep_hours}h</strong></p>
                <p>Average Study: <strong>${data.average_study_hours}h</strong></p>
                <p>Mood Breakdown:</p>
                <ul>${moodList}</ul>
                <p>Wellness Flags:</p>
                <ul>${flagsList}</ul>
            </div>
        `;
    } catch (err) {
        resultDiv.innerHTML = `<p>Something went wrong: ${err}</p>`;
    }
}

// ---- Chatbot ----
async function sendMessage() {
    const input = document.getElementById("chat-input");
    const message = input.value.trim();
    const chatWindow = document.getElementById("chat-window");

    if (!message) return;

    chatWindow.innerHTML += `<p class="user-msg"><strong>You:</strong> ${message}</p>`;
    input.value = "";
    chatWindow.innerHTML += `<p class="bot-msg" id="loading-msg"><strong>Advisor:</strong> Typing...</p>`;
    chatWindow.scrollTop = chatWindow.scrollHeight;

    try {
        const response = await fetch(`${API_BASE}/chat/${USER_ID}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        });
        const data = await response.json();

        document.getElementById("loading-msg").remove();

        if (data.error) {
            chatWindow.innerHTML += `<p class="bot-msg"><strong>Advisor:</strong> Error - ${data.error}</p>`;
        } else {
            chatWindow.innerHTML += `<div class="bot-msg"><strong>Advisor:</strong> ${marked.parse(data.reply)}</div>`;
        }
        chatWindow.scrollTop = chatWindow.scrollHeight;
    } catch (err) {
        document.getElementById("loading-msg").remove();
        chatWindow.innerHTML += `<p class="bot-msg">Something went wrong: ${err}</p>`;
    }
}
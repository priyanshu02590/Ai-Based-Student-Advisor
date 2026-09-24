const API_BASE = "";
let currentUser = null;

async function loadLinkedin() {
    const meResponse = await fetch(`${API_BASE}/me`, { credentials: "include" });
    const meData = await meResponse.json();

    if (meData.error) {
        window.location.href = "login.html";
        return;
    }

    currentUser = meData;

    const resultDiv = document.getElementById("linkedin-result");
    const response = await fetch(`${API_BASE}/linkedin/${meData.id}`, { credentials: "include" });
    const data = await response.json();

    if (data.error) {
        resultDiv.innerHTML = "<p>No LinkedIn data yet — fill the form below.</p>";
    } else {
        resultDiv.innerHTML = `
            <div class="result-card">
                <p class="score">Score: ${data.linkedin_score}/100</p>
                <p>Headline: ${data.headline}</p>
                <p>Skills: ${data.num_skills} | Connections: ${data.num_connections}</p>
                <p>Experience entries: ${data.num_experiences} | Endorsements: ${data.num_endorsements}</p>
            </div>
        `;
    }
}

document.getElementById("linkedin-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const body = {
        headline: document.getElementById("headline").value,
        has_profile_photo: document.getElementById("has_profile_photo").checked,
        has_summary: document.getElementById("has_summary").checked,
        num_skills: parseInt(document.getElementById("num_skills").value),
        num_connections: parseInt(document.getElementById("num_connections").value),
        num_experiences: parseInt(document.getElementById("num_experiences").value),
        num_endorsements: parseInt(document.getElementById("num_endorsements").value)
    };

    const response = await fetch(`${API_BASE}/linkedin/${currentUser.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(body)
    });
    const data = await response.json();

    if (data.linkedin_score !== undefined) {
        alert(`Saved! Your new score: ${data.linkedin_score}/100`);
        loadLinkedin();
    }
});

loadLinkedin();
const API_BASE = "";

async function loadGithubScore() {
    const meResponse = await fetch(`${API_BASE}/me`, { credentials: "include" });
    const meData = await meResponse.json();

    if (meData.error) {
        window.location.href = "login.html";
        return;
    }

    const resultDiv = document.getElementById("github-result");

    if (!meData.github_username) {
        resultDiv.innerHTML = "<p>No GitHub username linked to your account yet.</p>";
        return;
    }

    resultDiv.innerHTML = "<p>Loading your GitHub score...</p>";

    try {
        const response = await fetch(`${API_BASE}/digital-presence/${meData.github_username}`);
        const data = await response.json();

        if (data.error) {
            resultDiv.innerHTML = `<p>Error: ${data.error}</p>`;
            return;
        }

        resultDiv.innerHTML = `
            <div class="result-card">
                <img src="${data.avatar_url}" alt="avatar" width="80">
                <h2>${data.name || data.username}</h2>
                <p class="score">Score: ${data.digital_presence_score}/100</p>
                <p>Public Repos: ${data.public_repos}</p>
                <p>Followers: ${data.followers}</p>
                <p>Avg Contributions/Year: ${data.average_contributions_per_year}</p>
            </div>
        `;
    } catch (err) {
        resultDiv.innerHTML = `<p>Something went wrong: ${err}</p>`;
    }
}

loadGithubScore();
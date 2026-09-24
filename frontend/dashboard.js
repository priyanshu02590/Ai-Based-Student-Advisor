const API_BASE = "";
let currentUser = null;

function makeDonutChart(canvasId, score, color) {
    const ctx = document.getElementById(canvasId).getContext("2d");
    new Chart(ctx, {
        type: "doughnut",
        data: {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [color, "#e0e0e0"],
                borderWidth: 0
            }]
        },
        options: {
            cutout: "70%",
            plugins: { legend: { display: false }, tooltip: { enabled: false } }
        },
        plugins: [{
            id: "centerText",
            afterDraw: (chart) => {
                const { ctx, chartArea: { width, height } } = chart;
                ctx.save();
                ctx.font = "bold 20px Arial";
                ctx.fillStyle = "#2c3e50";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(`${score}`, width / 2, height / 2 + chart.chartArea.top);
                ctx.restore();
            }
        }]
    });
}

async function loadDashboard() {
    const meResponse = await fetch(`${API_BASE}/me`, { credentials: "include" });
    const meData = await meResponse.json();

    if (meData.error) {
        window.location.href = "login.html";
        return;
    }

    currentUser = meData;
    document.getElementById("welcome-msg").innerText = `Welcome, ${meData.name}!`;

    const insightResponse = await fetch(`${API_BASE}/habits/${meData.id}/weekly-insight`, { credentials: "include" });
    const insightData = await insightResponse.json();

    if (!insightData.error) {
        document.getElementById("avg-sleep-num").innerText = `${insightData.average_sleep_hours}h`;
        document.getElementById("avg-study-num").innerText = `${insightData.average_study_hours}h`;
        document.getElementById("topics-text").innerHTML = `<p>Recent Topics: ${insightData.topics_this_week.join(", ") || "None logged"}</p>`;
    }

    const habitsResponse = await fetch(`${API_BASE}/habits/${meData.id}`, { credentials: "include" });
    const habitsData = await habitsResponse.json();
    document.getElementById("checkin-count").innerText = Array.isArray(habitsData) ? habitsData.length : 0;

    let githubScore = 0;
    if (meData.github_username) {
        const ghResponse = await fetch(`${API_BASE}/digital-presence/${meData.github_username}`);
        const ghData = await ghResponse.json();
        if (!ghData.error) githubScore = Math.round(ghData.digital_presence_score);
    }
    makeDonutChart("githubChart", githubScore, "#2c3e50");

    let linkedinScore = 0;
    const liResponse = await fetch(`${API_BASE}/linkedin/${meData.id}`, { credentials: "include" });
    const liData = await liResponse.json();
    if (!liData.error) linkedinScore = Math.round(liData.linkedin_score);
    makeDonutChart("linkedinChart", linkedinScore, "#0077b5");

    const checkResponse = await fetch(`${API_BASE}/habits/${meData.id}/check-today`, { credentials: "include" });
    const checkData = await checkResponse.json();
    if (!checkData.already_logged) {
        document.getElementById("daily-checkin").style.display = "block";
    }
}

document.getElementById("checkin-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const body = {
        mood: document.getElementById("mood").value,
        study_hours: parseFloat(document.getElementById("study_hours").value),
        sleep_hours: parseFloat(document.getElementById("sleep_hours").value),
        topics_studied: document.getElementById("topics_studied").value,
        tasks_completed: document.getElementById("tasks_completed").value
    };

    const response = await fetch(`${API_BASE}/habits/${currentUser.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(body)
    });
    const data = await response.json();

    if (data.id) {
        alert("Today's check-in saved!");
        document.getElementById("daily-checkin").style.display = "none";
        location.reload();
    }
});

async function logout() {
    await fetch(`${API_BASE}/logout`, { method: "POST", credentials: "include" });
    window.location.href = "login.html";
}

loadDashboard();
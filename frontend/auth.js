const API_BASE = "";

const signupForm = document.getElementById("signup-form");
if (signupForm) {
    signupForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("name").value;
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;
        const github_username = document.getElementById("github_username").value;

        try {
            const response = await fetch(`${API_BASE}/signup`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ name, username, password, github_username })
            });
            const data = await response.json();

            if (data.error) {
                document.getElementById("error-msg").innerText = data.error;
                return;
            }

            window.location.href = "dashboard.html";
        } catch (err) {
            document.getElementById("error-msg").innerText = "Something went wrong.";
        }
    });
}

const loginForm = document.getElementById("login-form");
if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        try {
            const response = await fetch(`${API_BASE}/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ username, password })
            });
            const data = await response.json();

            if (data.error) {
                document.getElementById("error-msg").innerText = data.error;
                return;
            }

            window.location.href = "dashboard.html";
        } catch (err) {
            document.getElementById("error-msg").innerText = "Something went wrong.";
        }
    });
}
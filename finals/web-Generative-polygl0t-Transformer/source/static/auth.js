document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.getElementById("registerForm");
    const registerUsername = document.getElementById("registerUsername");
    const registerError = document.getElementById("registerError");
    const registerSuccess = document.getElementById("registerSuccess");
    const generatedPassword = document.getElementById("generatedPassword");
    const copyPasswordButton = document.getElementById("copyPasswordButton");
    const continueToLogin = document.getElementById("continueToLogin");
    const copyFeedback = document.getElementById("copyFeedback");
    const loginForm = document.getElementById("loginForm");
    const loginUsername = document.getElementById("loginUsername");
    const loginPassword = document.getElementById("loginPassword");
    const loginError = document.getElementById("loginError");
    const authTabs = Array.from(document.querySelectorAll(".auth-tab"));
    const authPanes = Array.from(document.querySelectorAll("[data-auth-pane]"));

    function errorMessage(code) {
        return window.GPT.t(code, window.GPT.t("requestFailed"));
    }

    function setAuthPane(nextPane) {
        authTabs.forEach((button) => {
            button.classList.toggle("is-active", button.dataset.authTarget === nextPane);
        });
        authPanes.forEach((pane) => {
            pane.hidden = pane.dataset.authPane !== nextPane;
        });
        if (copyFeedback) {
            copyFeedback.hidden = true;
        }
    }

    async function handleRegister(event) {
        event.preventDefault();
        registerError.hidden = true;
        registerSuccess.hidden = true;

        const response = await fetch("/api/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: registerUsername.value.trim()
            })
        });
        const data = await response.json();
        if (!response.ok) {
            registerError.hidden = false;
            registerError.textContent = errorMessage(data.error);
            return;
        }

        generatedPassword.textContent = data.password;
        registerSuccess.hidden = false;
        if (copyFeedback) {
            copyFeedback.hidden = true;
        }
        loginUsername.value = data.username;
        loginPassword.value = data.password;
    }

    async function handleLogin(event) {
        event.preventDefault();
        loginError.hidden = true;

        const response = await fetch("/api/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: loginUsername.value.trim(),
                password: loginPassword.value
            })
        });
        const data = await response.json();
        if (!response.ok) {
            loginError.hidden = false;
            loginError.textContent = errorMessage(data.error);
            return;
        }

        window.location.href = "/";
    }

    authTabs.forEach((button) => {
        button.addEventListener("click", () => setAuthPane(button.dataset.authTarget));
    });

    setAuthPane(window.PAGE_DATA.authMode || "register");

    registerForm.addEventListener("submit", (event) => {
        handleRegister(event).catch(() => {
            registerError.hidden = false;
            registerError.textContent = window.GPT.t("requestFailed");
        });
    });

    loginForm.addEventListener("submit", (event) => {
        handleLogin(event).catch(() => {
            loginError.hidden = false;
            loginError.textContent = window.GPT.t("requestFailed");
        });
    });

    copyPasswordButton.addEventListener("click", async () => {
        try {
            await navigator.clipboard.writeText(generatedPassword.textContent || "");
            copyFeedback.hidden = false;
            copyFeedback.textContent = window.GPT.t("copyPasswordSuccess");
        } catch {
            copyFeedback.hidden = false;
            copyFeedback.textContent = window.GPT.t("copyPasswordFallback");
        }
    });

    continueToLogin.addEventListener("click", () => {
        setAuthPane("login");
        loginPassword.focus();
    });
});

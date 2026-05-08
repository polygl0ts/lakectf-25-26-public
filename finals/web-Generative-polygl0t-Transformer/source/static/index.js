document.addEventListener("DOMContentLoaded", () => {
    const askForm = document.getElementById("askForm");
    const promptInput = document.getElementById("promptInput");
    const historyList = document.getElementById("historyList");
    const historyEmpty = document.getElementById("historyEmpty");
    const errorText = document.getElementById("formError");
    const targetButtons = Array.from(document.querySelectorAll(".tab-button"));
    let target = "human";

    function errorMessage(code) {
        return window.GPT.t(code, window.GPT.t("requestFailed"));
    }

    function setTarget(nextTarget) {
        target = nextTarget;
        targetButtons.forEach((button) => {
            button.classList.toggle("is-active", button.dataset.target === nextTarget);
        });
    }

    async function loadHistory() {
        if (!historyList || !historyEmpty) {
            return;
        }
        const response = await fetch("/api/history");
        if (!response.ok) {
            return;
        }
        const data = await response.json();
        historyList.innerHTML = "";
        const items = data.items || [];
        historyEmpty.hidden = items.length > 0;

        items.forEach((item) => {
            const row = document.createElement("a");
            row.href = item.url;
            row.className = "history-item";
            row.innerHTML = `
                <div class="history-top">
                    <span class="status-badge">${window.GPT.t(window.GPT.statusKey(item.status))}</span>
                    <span class="status-note">${item.target || "-"}</span>
                </div>
                <div class="history-main">${window.GPT.escapeHtml(item.id)}</div>
                <div class="status-note">${window.GPT.escapeHtml(item.locale.toUpperCase())}</div>
            `;
            historyList.appendChild(row);
        });
    }

    async function submitPrompt(event) {
        event.preventDefault();
        errorText.hidden = true;
        const prompt = promptInput.value.trim();
        if (!prompt) {
            errorText.hidden = false;
            errorText.textContent = errorMessage("missing_prompt");
            return;
        }

        const createResponse = await fetch("/api/chats", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ prompt })
        });
        const createData = await createResponse.json();
        if (!createResponse.ok) {
            errorText.hidden = false;
            errorText.textContent = errorMessage(createData.error);
            return;
        }

        const dispatchResponse = await fetch("/api/dispatch", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                target,
                url: `/chat/${createData.id}`
            })
        });
        const dispatchData = await dispatchResponse.json();
        if (!dispatchResponse.ok) {
            errorText.hidden = false;
            errorText.textContent = errorMessage(dispatchData.error);
            return;
        }

        window.location.href = createData.url;
    }

    if (askForm) {
        targetButtons.forEach((button) => {
            button.addEventListener("click", () => setTarget(button.dataset.target));
        });
        askForm.addEventListener("submit", (event) => {
            submitPrompt(event).catch(() => {
                errorText.hidden = false;
                errorText.textContent = window.GPT.t("requestFailed");
            });
        });

        setTarget("human");
        loadHistory().catch(() => {});
    }
});

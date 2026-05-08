document.addEventListener("DOMContentLoaded", () => {
    const claimNextButton = document.getElementById("claimNext");
    const submitAnswer = document.getElementById("submitAnswer");
    const abandonClaim = document.getElementById("abandonClaim");
    const answerDraft = document.getElementById("answerDraft");

    const idleView = document.getElementById("claimIdleView");
    const activeView = document.getElementById("claimActiveView");
    const statusPill = document.getElementById("claimStatusPill");

    const claimLocale = document.getElementById("claimLocale");
    const claimPrompt = document.getElementById("claimPrompt");
    const claimTimer = document.getElementById("claimTimer");
    const claimUrl = document.getElementById("claimUrl");

    const idleError = document.getElementById("idleError");
    const activeError = document.getElementById("activeError");
    const activeInfo = document.getElementById("activeInfo");

    const idleQueueCount = document.getElementById("idleQueueCount");
    const idleQueueHint = document.getElementById("idleQueueHint");

    const queueList = document.getElementById("queueList");
    const queueEmpty = document.getElementById("queueEmpty");
    const queueTabCount = document.getElementById("queueTabCount");

    const answeredList = document.getElementById("answeredList");
    const answeredEmpty = document.getElementById("answeredEmpty");
    const answeredTabCount = document.getElementById("answeredTabCount");

    const otherClaimedSection = document.getElementById("otherClaimedSection");
    const otherClaimedList = document.getElementById("otherClaimedList");

    const tabButtons = document.querySelectorAll(".dashboard-tabs [data-tab]");
    const tabPanes = document.querySelectorAll(".tab-pane");

    let activeClaim = null;
    let lastQueueData = { queue: [], claimed: [], history: [] };

    function showIdleError(messageKey) {
        if (!messageKey) {
            idleError.hidden = true;
            idleError.textContent = "";
            return;
        }
        idleError.hidden = false;
        idleError.textContent = window.GPT.t(messageKey);
    }

    function showActiveError(messageKey) {
        if (!messageKey) {
            activeError.hidden = true;
            activeError.textContent = "";
            return;
        }
        activeError.hidden = false;
        activeError.textContent = window.GPT.t(messageKey);
    }

    function showActiveInfo(messageKey) {
        if (!messageKey) {
            activeInfo.hidden = true;
            activeInfo.textContent = "";
            return;
        }
        activeInfo.hidden = false;
        activeInfo.textContent = window.GPT.t(messageKey);
    }

    function setStatus(state) {
        statusPill.classList.remove("is-typing", "is-idle", "is-error");
        if (state === "typing") {
            statusPill.classList.add("is-typing");
            statusPill.textContent = window.GPT.t("dashStatusActive");
        } else if (state === "error") {
            statusPill.classList.add("is-error");
            statusPill.textContent = window.GPT.t("dashStatusError");
        } else {
            statusPill.classList.add("is-idle");
            statusPill.textContent = window.GPT.t("dashStatusIdle");
        }
    }

    function renderActiveClaim() {
        const hasClaim = Boolean(activeClaim);
        idleView.hidden = hasClaim;
        activeView.hidden = !hasClaim;
        if (!hasClaim) {
            answerDraft.value = "";
            claimTimer.textContent = "";
            claimUrl.textContent = "";
            claimPrompt.innerHTML = "";
            setStatus("idle");
            showActiveError(null);
            showActiveInfo(null);
            return;
        }
        claimLocale.textContent = (activeClaim.locale || "").toUpperCase();
        claimPrompt.innerHTML = window.GPT.renderRichText(activeClaim.promptHtml || "");
        claimUrl.textContent = activeClaim.url || "";
        setStatus("typing");
    }

    function buildHistoryItem(item, opts = {}) {
        const row = document.createElement("div");
        row.className = "history-item";
        const localeTag = window.GPT.escapeHtml((item.locale || "").toUpperCase());
        const author = item.claimedBy || item.answerAuthor || "";
        const body = item.answerHtml || item.promptHtml || "";
        const labelKey = opts.showAnswer ? "answerPreviewLabel" : "promptPreviewLabel";
        const label = window.GPT.t(labelKey);
        row.innerHTML = `
            <div class="history-top">
                <span class="status-badge locale-tag">${localeTag}</span>
                <span class="status-note">${window.GPT.escapeHtml(author)}</span>
            </div>
            <div class="message-label">${window.GPT.escapeHtml(label)}</div>
            <div class="rich-text">${window.GPT.renderRichText(body)}</div>
        `;
        return row;
    }

    function renderQueuePane(data) {
        const queue = data.queue || [];
        const claimed = data.claimed || [];
        const history = data.history || [];

        queueTabCount.textContent = String(queue.length);
        answeredTabCount.textContent = String(history.length);

        queueEmpty.hidden = queue.length > 0;
        queueList.innerHTML = "";
        queue.forEach((item) => queueList.appendChild(buildHistoryItem(item)));

        const othersClaimed = activeClaim
            ? claimed.filter((item) => item.id !== activeClaim.id)
            : claimed;
        otherClaimedSection.hidden = othersClaimed.length === 0;
        otherClaimedList.innerHTML = "";
        othersClaimed.forEach((item) => otherClaimedList.appendChild(buildHistoryItem(item)));

        answeredEmpty.hidden = history.length > 0;
        answeredList.innerHTML = "";
        history.forEach((item) => answeredList.appendChild(buildHistoryItem(item, { showAnswer: true })));

        idleQueueCount.textContent = String(queue.length);
        idleQueueHint.textContent = queue.length > 0
            ? window.GPT.t("queueHasItemsHint")
            : window.GPT.t("queueIdleHint");
    }

    async function loadDashboard() {
        try {
            const response = await fetch("/api/dashboard/queue");
            if (!response.ok) {
                return;
            }
            const data = await response.json();
            lastQueueData = data;
            renderQueuePane(data);
        } catch (err) {
            // ignore transient poll failures
        }
    }

    async function claimNext() {
        showIdleError(null);
        let response;
        try {
            response = await fetch("/api/dashboard/claim-next", { method: "POST" });
        } catch (err) {
            showIdleError("requestFailed");
            return;
        }
        let data = {};
        try {
            data = await response.json();
        } catch (err) {
            // ignore parse errors
        }
        if (!response.ok) {
            showIdleError("requestFailed");
            return;
        }
        if (!data.claim) {
            showIdleError("noQueueToClaim");
            return;
        }
        activeClaim = data.claim;
        renderActiveClaim();
        renderQueuePane(lastQueueData);
        answerDraft.focus();
    }

    async function heartbeat() {
        if (!activeClaim) return;
        let response;
        try {
            response = await fetch("/api/dashboard/heartbeat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    id: activeClaim.id,
                    claimToken: activeClaim.claimToken,
                    draft: answerDraft.value
                })
            });
        } catch (err) {
            return;
        }
        if (!response.ok) {
            activeClaim = null;
            renderActiveClaim();
            showIdleError("claimExpired");
            loadDashboard();
            return;
        }
        const data = await response.json().catch(() => ({}));
        if (data.claimUntil) {
            activeClaim.claimUntil = data.claimUntil;
        }
    }

    async function finalizeAnswer() {
        if (!activeClaim) {
            showActiveError("noActiveClaim");
            return;
        }
        if (!answerDraft.value.trim()) {
            showActiveError("emptyAnswer");
            return;
        }
        showActiveError(null);
        showActiveInfo("sending");
        submitAnswer.disabled = true;
        let response;
        try {
            response = await fetch("/api/dashboard/answer", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    id: activeClaim.id,
                    claimToken: activeClaim.claimToken,
                    answer: answerDraft.value
                })
            });
        } catch (err) {
            submitAnswer.disabled = false;
            showActiveInfo(null);
            showActiveError("requestFailed");
            return;
        }
        submitAnswer.disabled = false;
        showActiveInfo(null);
        if (!response.ok) {
            showActiveError("claimExpired");
            return;
        }
        activeClaim = null;
        renderActiveClaim();
        loadDashboard();
    }

    async function releaseClaim() {
        if (!activeClaim) return;
        const claim = activeClaim;
        abandonClaim.disabled = true;
        try {
            await fetch("/api/dashboard/release", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id: claim.id, claimToken: claim.claimToken })
            });
        } catch (err) {
            // ignore: we still clear locally
        }
        abandonClaim.disabled = false;
        activeClaim = null;
        renderActiveClaim();
        loadDashboard();
    }

    function switchTab(name) {
        tabButtons.forEach((btn) => {
            btn.classList.toggle("is-active", btn.dataset.tab === name);
        });
        tabPanes.forEach((pane) => {
            pane.hidden = pane.dataset.pane !== name;
        });
    }

    tabButtons.forEach((btn) => {
        btn.addEventListener("click", () => switchTab(btn.dataset.tab));
    });

    claimNextButton.addEventListener("click", () => {
        claimNextButton.disabled = true;
        claimNext().finally(() => {
            claimNextButton.disabled = false;
        });
    });

    submitAnswer.addEventListener("click", () => {
        finalizeAnswer();
    });

    abandonClaim.addEventListener("click", () => {
        releaseClaim();
    });

    let typingDebounce = null;
    answerDraft.addEventListener("input", () => {
        showActiveError(null);
        if (typingDebounce) clearTimeout(typingDebounce);
        typingDebounce = window.setTimeout(() => {
            heartbeat();
        }, 600);
    });

    window.setInterval(() => {
        if (activeClaim && activeClaim.claimUntil) {
            const remaining = Math.max(0, activeClaim.claimUntil - Math.floor(Date.now() / 1000));
            claimTimer.textContent = `${window.GPT.t("timeLeft")} ${window.GPT.formatTime(remaining)}`;
            if (remaining === 0) {
                heartbeat();
            }
        }
    }, 500);

    window.setInterval(() => {
        if (activeClaim) {
            heartbeat();
        }
        loadDashboard();
    }, 5000);

    setStatus("idle");
    renderActiveClaim();
    loadDashboard();
});

function sanitizeChat(chat) {
    try {
        chat.prompt = DOMPurify.sanitize(chat.prompt);
        chat.answer = DOMPurify.sanitize(chat.answer);
    } catch (err) {
        console.log(err);
    }
}

function renderChat(chat) {
    sanitizeChat(chat);

    const promptContent = document.getElementById("promptContent");
    const answerContent = document.getElementById("answerContent");
    const answerMeta = document.getElementById("answerMeta");
    const chatStatus = document.getElementById("chatStatus");
    const queuePosition = document.getElementById("queuePosition");
    const assistantBubble = answerContent.closest(".chat-bubble");

    promptContent.innerHTML = chat.prompt;
    chatStatus.textContent = window.GPT.t(window.GPT.statusKey(chat.status));
    queuePosition.textContent = "";
    if ((chat.status === "queued" || chat.status === "bot_pending") && chat.queuePosition) {
        queuePosition.textContent = `${window.GPT.t("queuePosition")}: ${chat.queuePosition}`;
    } else if (chat.status === "claimed") {
        queuePosition.textContent = window.GPT.t("typingState");
    } else if (chat.status === "bot_processing") {
        queuePosition.textContent = window.GPT.t("botVisiting");
    }

    const hasAnswer = chat.status === "answered" && chat.answer;
    const isPending = chat.status === "claimed" || chat.status === "bot_pending" || chat.status === "bot_processing";
    assistantBubble.hidden = !hasAnswer && !isPending;
    assistantBubble.classList.toggle("is-pending", !hasAnswer && isPending);

    if (hasAnswer) {
        answerContent.innerHTML = chat.answer;
        answerMeta.textContent = chat.answerAuthor ? `${window.GPT.t("answerFrom")} ${chat.answerAuthor}` : "";
    } else if (isPending) {
        answerContent.innerHTML = `<span class="typing-dots"><span></span><span></span><span></span></span>`;
        answerMeta.textContent = "";
    } else {
        answerContent.innerHTML = "";
        answerMeta.textContent = "";
    }
}

function refresh() {
    fetch(`/api/chat?id=${window.PAGE_DATA.chatId}`).then((r) => r.text()).then((body) => {
        renderChat(JSON.parse(body));
    });
}

setTimeout(refresh, 1000);
setInterval(refresh, 3000);

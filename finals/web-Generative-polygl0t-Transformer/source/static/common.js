window.GPT_DEFAULT_LANG = {
    siteTitle: "Generative polygl0ts Transformer (GPT)",
    inspiredByPrefix: "Inspired by",
    adminBadge: "admin",
    dashboardLink: "Dashboard",
    logoutButton: "Log out",
    registerLink: "Register",
    loginLink: "Log in",
    authTitle: "Access",
    authBody: "Username creates an account. Password is shown once.",
    authEyebrow: "Login layer",
    registerTab: "Create account",
    loginTab: "I already have a password",
    registerTitle: "Register",
    loginTitle: "Log in",
    usernameLabel: "Username",
    passwordLabel: "Password",
    usernamePlaceholder: "teamname",
    passwordPlaceholder: "paste your saved password",
    usernameRules: "Use 3-24 lowercase letters, digits, or underscores.",
    registerButton: "Generate password",
    loginButton: "Log in",
    registerSuccessTitle: "Registration complete",
    registerSuccessBody: "Password shown once. Store it.",
    registerResultTitle: "Account created",
    registerResultBody: "Password shown once. Store it.",
    generatedPasswordLabel: "Generated password",
    copyPasswordButton: "Copy password",
    continueToLogin: "Continue to login",
    copyPasswordSuccess: "Password copied.",
    copyPasswordFallback: "Copy it manually from the box above.",
    savePasswordWarning: "Lost means new account.",
    requestFailed: "The request failed.",
    missing_prompt: "Write a question first.",
    prompt_too_long: "That question is too long.",
    rate_limited: "Too many requests. Slow down and try again soon.",
    invalid_username: "Choose 3-24 lowercase letters, digits, or underscores.",
    username_taken: "That username already exists.",
    missing_username: "Enter your username.",
    missing_password: "Enter your password.",
    invalid_credentials: "That username or password is incorrect.",
    login_required: "Log in first.",
    admin_required: "Admin access is required.",
    claim_expired: "This claim expired.",
    homeSubtitle: "GPT got banned from the CTF, but don't worry we got ya",
    homeBody: "you can ask for solutions, flags, ctfd admin creds, maybe we'll help",
    cloudflareHintTitle: "hack on remote setup pls",
    cloudflareHint: "source code can be read but I recommend testing on remote, using Cloudflare proxy for this page is relevant here (default free config)",
    chatYou: "You",
    chatAssistant: "polygl0ts",
    abandonClaimHint: "Release the claim back to the queue so anyone can grab it.",
    ctaEyebrow: "Access",
    ctaTitle: "Enter the relay",
    ctaBody: "Create a username. Keep the password.",
    continueButton: "Continue",
    dashboardTitle: "Answer a question",
    dashboardEyebrow: "polygl0ts console",
    dashboardBody: "Pick the next question from the queue. You get 90 seconds per claim, extended while you keep typing.",
    dashStatusActive: "You are answering",
    dashStatusIdle: "Idle",
    dashStatusError: "Lost claim",
    queueCountLabel: "In queue",
    queueIdleHint: "Queue empty.",
    queueHasItemsHint: "Players are waiting. Grab one.",
    queueTab: "Queue",
    answeredTab: "Answered",
    otherClaimedLabel: "Being answered by someone else",
    playerQuestionLabel: "Player question",
    promptPreviewLabel: "Prompt",
    answerPreviewLabel: "Answer",
    abandonClaim: "Put back in queue",
    submitAnswer: "Send answer",
    claimNext: "Take next question",
    draftLabel: "Your answer (bold / italic / headings allowed)",
    draftPlaceholder: "hint, caveat, next step",
    noQueue: "Queue is empty.",
    noAnswered: "No answered questions yet.",
    noQueueToClaim: "Nothing to claim right now.",
    noActiveClaim: "Take a question before sending an answer.",
    emptyAnswer: "Write something before hitting send.",
    sending: "Sending..."
};

window.GPT = {
    allowedTags: ["b", "strong", "i", "em", "u", "p", "br", "h1", "h2", "h3", "h4", "ul", "ol", "li", "blockquote", "code"],
    t(key, fallback) {
        if (window.GPT_LANG && Object.prototype.hasOwnProperty.call(window.GPT_LANG, key)) {
            return window.GPT_LANG[key];
        }
        if (Object.prototype.hasOwnProperty.call(window.GPT_DEFAULT_LANG, key)) {
            return window.GPT_DEFAULT_LANG[key];
        }
        return fallback || key;
    },
    applyTranslations(root = document) {
        root.querySelectorAll("[data-i18n]").forEach((element) => {
            element.textContent = window.GPT.t(element.dataset.i18n, element.textContent);
        });
        root.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
            element.placeholder = window.GPT.t(element.dataset.i18nPlaceholder, element.placeholder || "");
        });
        root.querySelectorAll("[data-i18n-title]").forEach((element) => {
            element.title = window.GPT.t(element.dataset.i18nTitle, element.title || "");
        });
    },
    escapeHtml(value) {
        const div = document.createElement("div");
        div.textContent = value || "";
        return div.innerHTML;
    },
    renderRichText(value) {
        if (window.DOMPurify) {
            return window.DOMPurify.sanitize(value || "", {
                ALLOWED_TAGS: window.GPT.allowedTags
            });
        }
        return window.GPT.escapeHtml(value || "");
    },
    statusKey(status) {
        const mapping = {
            draft: "statusDraft",
            queued: "statusQueued",
            claimed: "statusTyping",
            answered: "statusAnswered",
            bot_pending: "statusBotPending",
            bot_processing: "statusBotPending",
            bot_failed: "statusBotFailed"
        };
        return mapping[status] || "statusLoading";
    },
    formatTime(secondsRemaining) {
        const safe = Math.max(0, secondsRemaining);
        const minutes = Math.floor(safe / 60);
        const seconds = safe % 60;
        return `${minutes}:${String(seconds).padStart(2, "0")}`;
    }
};

document.addEventListener("DOMContentLoaded", () => {
    window.GPT.applyTranslations();
});

// ============================================================
// PediaGuide AI - Frontend
// Connects the UI with the FastAPI backend
// ============================================================


// ============================================================
// VARIABLES
// ============================================================

let conversationId = null;
let isSending = false;


// ============================================================
// DOM ELEMENTS
// ============================================================

const newChatButton = document.getElementById("new-chat-btn");
const chatHistory = document.getElementById("chat-history");

const welcome = document.getElementById("welcome");
const chatMessages = document.getElementById("chat-messages");

const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendButton = document.getElementById("send-btn");

const exampleQuestions = document.querySelectorAll(".example-question");


// ============================================================
// START APPLICATION
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
    loadConversations();
    setupExampleQuestions();
    setupTextarea();
});


// ============================================================
// LOAD CONVERSATION LIST
// ============================================================

async function loadConversations() {

    try {

        const response = await fetch("/conversations");

        if (!response.ok) {
            throw new Error("Could not load conversations.");
        }

        const data = await response.json();

        displayConversationList(data.conversations);

    } catch (error) {

        console.error("Conversation loading error:", error);

        chatHistory.innerHTML = `
            <div class="empty-history">
                Unable to load conversations.
            </div>
        `;
    }
}

// ============================================================
// DISPLAY CONVERSATIONS IN SIDEBAR
// ============================================================

function displayConversationList(conversations) {

    if (!conversations || conversations.length === 0) {

        chatHistory.innerHTML = `
            <div class="empty-history">
                No conversations yet.
            </div>
        `;

        return;
    }


    chatHistory.innerHTML = "";


    conversations.forEach(conversation => {

        const item = document.createElement("div");

        item.className = "history-item-wrapper";


        if (conversation.conversation_id === conversationId) {
            item.classList.add("active");
        }


        // Conversation button
        const chatButton = document.createElement("button");

        chatButton.type = "button";
        chatButton.className = "history-item";


        const title = conversation.title || "New conversation";

        const ageText =
            conversation.age_months !== null &&
            conversation.age_months !== undefined
                ? formatAge(conversation.age_months)
                : "";


        chatButton.innerHTML = `
            <span class="history-title">
                ${escapeHtml(title)}
            </span>

            ${
                ageText
                    ? `<span class="history-age">
                        ${escapeHtml(ageText)}
                       </span>`
                    : ""
            }
        `;


        chatButton.addEventListener("click", () => {
            openConversation(conversation.conversation_id);
        });


        // Delete button
        const deleteButton = document.createElement("button");

        deleteButton.type = "button";
        deleteButton.className = "delete-chat-btn";

        deleteButton.innerHTML = "×";

        deleteButton.title = "Delete conversation";


        deleteButton.addEventListener("click", event => {

            event.stopPropagation();

            deleteChat(conversation.conversation_id);
        });


        item.appendChild(chatButton);
        item.appendChild(deleteButton);

        chatHistory.appendChild(item);
    });
}

// ============================================================
// DELETE CHAT
// ============================================================

async function deleteChat(id) {

    const confirmed = confirm(
        "Are you sure you want to delete this conversation?"
    );


    if (!confirmed) {
        return;
    }


    try {

        const response = await fetch(
            `/conversations/${id}`,
            {
                method: "DELETE"
            }
        );


        if (!response.ok) {

            throw new Error(
                "Could not delete conversation."
            );
        }


        // If the deleted conversation is currently open
        if (conversationId === id) {

            conversationId = null;

            clearMessages();

            showWelcome();

            chatInput.value = "";
        }


        // Refresh sidebar
        await loadConversations();


    } catch (error) {

        console.error("Delete conversation error:", error);

        alert(
            "Unable to delete this conversation. Please try again."
        );
    }
}

// ============================================================
// OPEN SAVED CONVERSATION
// ============================================================

async function openConversation(id) {

    if (isSending) {
        return;
    }


    try {

        const response = await fetch(`/conversations/${id}`);


        if (!response.ok) {
            throw new Error("Could not open conversation.");
        }


        const conversation = await response.json();


        conversationId = conversation.conversation_id;


        clearMessages();

        hideWelcome();


        conversation.messages.forEach(message => {

            if (message.role === "user") {

                addMessage("user", message.content);

            } else if (message.role === "assistant") {

                addMessage(
                    "assistant",
                    message.content,
                    message.sources || []
                );
            }
        });


        loadConversations();

        scrollToBottom();


    } catch (error) {

        console.error("Conversation opening error:", error);

        addMessage(
            "assistant",
            "I couldn't open this conversation. Please try again."
        );
    }
}


// ============================================================
// NEW CHAT
// ============================================================

function startNewChat() {

    if (isSending) {
        return;
    }


    conversationId = null;


    clearMessages();

    showWelcome();

    chatInput.value = "";

    chatInput.focus();

    loadConversations();
}


// ============================================================
// SEND MESSAGE
// ============================================================

chatForm.addEventListener("submit", async event => {

    event.preventDefault();


    if (isSending) {
        return;
    }


    const message = chatInput.value.trim();


    if (!message) {
        return;
    }


    await sendMessage(message);
});


// ============================================================
// SEND MESSAGE TO FASTAPI
// ============================================================

async function sendMessage(message) {

    isSending = true;

    setSendingState(true);


    hideWelcome();


    // Show user's message immediately
    addMessage("user", message);


    // Clear input
    chatInput.value = "";

    resizeTextarea();


    // Show thinking indicator
    const thinkingElement = addThinkingIndicator();


    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                conversation_id: conversationId,
                message: message
            })
        });


        const data = await response.json();


        // Remove thinking indicator
        thinkingElement.remove();


        // Backend error
        if (!response.ok) {

            const errorMessage =
                data.detail ||
                "Something went wrong while processing your question.";

            addMessage("assistant", errorMessage);

            return;
        }


        // ----------------------------------------------------
        // Backend says age is required
        // ----------------------------------------------------

        if (data.needs_age) {

            addMessage(
                "assistant",
                data.answer
            );

            return;
        }


        // ----------------------------------------------------
        // Save conversation ID
        // ----------------------------------------------------

        if (data.conversation_id) {

            conversationId = data.conversation_id;
        }


        // ----------------------------------------------------
        // Display AI answer
        // ----------------------------------------------------

        addMessage(
            "assistant",
            data.answer,
            data.sources || []
        );


        // Update sidebar
        await loadConversations();


    } catch (error) {

        console.error("Chat error:", error);


        // Remove thinking indicator if it still exists
        if (thinkingElement && thinkingElement.parentNode) {
            thinkingElement.remove();
        }


        addMessage(
            "assistant",
            "I'm sorry, something went wrong while connecting to PediaGuide. Please try again."
        );


    } finally {

        isSending = false;

        setSendingState(false);

        chatInput.focus();

        scrollToBottom();
    }
}


// ============================================================
// ADD MESSAGE
// ============================================================

function addMessage(role, text, sources = []) {

    const message = document.createElement("div");

    message.className = `message ${role}`;


    const content = document.createElement("div");

    content.className = "message-content";


    // Convert simple Markdown-style formatting
    content.innerHTML = formatMessage(text);


    // Add sources for assistant responses
    if (role === "assistant" && sources.length > 0) {

        content.appendChild(createSources(sources));
    }


    message.appendChild(content);

    chatMessages.appendChild(message);


    scrollToBottom();
}


// ============================================================
// FORMAT AI MESSAGE
// ============================================================

function formatMessage(text) {

    if (!text) {
        return "";
    }

    const markdownHtml = marked.parse(text);

    return DOMPurify.sanitize(markdownHtml);
}


// ============================================================
// CREATE SOURCES SECTION
// ============================================================

function createSources(sources) {

    const container = document.createElement("div");

    container.className = "sources";


    const title = document.createElement("div");

    title.className = "sources-title";

    title.textContent = "Medical Sources";


    container.appendChild(title);


    sources.forEach((source, index) => {

        const sourceItem = document.createElement("div");

        sourceItem.className = "source-item";


        const documentName =
            source.document ||
            source.document_id ||
            "Medical document";


        const page =
            source.page ||
            source.page_number;


        sourceItem.innerHTML = `
            <span class="source-name">
                ${escapeHtml(documentName)}
            </span>

            ${
                page
                    ? `<span class="source-page">
                        · Page ${escapeHtml(String(page))}
                       </span>`
                    : ""
            }
        `;


        container.appendChild(sourceItem);
    });


    return container;
}


// ============================================================
// THINKING INDICATOR
// ============================================================

function addThinkingIndicator() {

    const message = document.createElement("div");

    message.className = "message assistant";


    message.innerHTML = `
        <div class="thinking">
            <span class="thinking-dot"></span>
            <span class="thinking-dot"></span>
            <span class="thinking-dot"></span>
        </div>
    `;


    chatMessages.appendChild(message);


    scrollToBottom();


    return message;
}


// ============================================================
// CLEAR CHAT MESSAGES
// ============================================================

function clearMessages() {

    chatMessages.innerHTML = "";
}


// ============================================================
// SHOW / HIDE WELCOME
// ============================================================

function showWelcome() {

    welcome.style.display = "block";
}


function hideWelcome() {

    welcome.style.display = "none";
}


// ============================================================
// SEND BUTTON STATE
// ============================================================

function setSendingState(sending) {

    sendButton.disabled = sending;

    chatInput.disabled = sending;


    if (sending) {

        sendButton.textContent = "...";

    } else {

        sendButton.textContent = "↑";
    }
}


// ============================================================
// EXAMPLE QUESTIONS
// ============================================================

function setupExampleQuestions() {

    exampleQuestions.forEach(button => {

        button.addEventListener("click", () => {

            const question = button.dataset.question;


            if (!question) {
                return;
            }


            chatInput.value = question;

            resizeTextarea();

            chatInput.focus();
        });
    });
}


// ============================================================
// TEXTAREA BEHAVIOR
// ============================================================

function setupTextarea() {

    chatInput.addEventListener("input", resizeTextarea);


    chatInput.addEventListener("keydown", event => {

        // Enter = send
        // Shift + Enter = new line

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            chatForm.requestSubmit();
        }
    });
}


// ============================================================
// RESIZE TEXTAREA
// ============================================================

function resizeTextarea() {

    chatInput.style.height = "auto";


    const height = Math.min(
        chatInput.scrollHeight,
        130
    );


    chatInput.style.height = `${height}px`;
}


// ============================================================
// SCROLL TO BOTTOM
// ============================================================

function scrollToBottom() {

    requestAnimationFrame(() => {

        const chatArea = document.getElementById("chat-area");

        chatArea.scrollTop = chatArea.scrollHeight;
    });
}


// ============================================================
// FORMAT AGE
// ============================================================

function formatAge(months) {

    if (months === 0) {
        return "Newborn";
    }


    if (months < 12) {

        return `${months} month${months === 1 ? "" : "s"} old`;
    }


    const years = Math.floor(months / 12);

    const remainingMonths = months % 12;


    if (remainingMonths === 0) {

        return `${years} year${years === 1 ? "" : "s"} old`;
    }


    return `${years} year${years === 1 ? "" : "s"} ${remainingMonths} month${remainingMonths === 1 ? "" : "s"} old`;
}


// ============================================================
// HTML ESCAPING
// Prevents raw HTML from being inserted into the page
// ============================================================

function escapeHtml(value) {

    const div = document.createElement("div");

    div.textContent = value ?? "";

    return div.innerHTML;
}


// ============================================================
// BUTTON EVENTS
// ============================================================

newChatButton.addEventListener("click", startNewChat);
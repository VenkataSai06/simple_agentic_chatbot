const messageInput =
    document.getElementById("messageInput");

const sendButton =
    document.getElementById("sendButton");

const chatContainer =
    document.getElementById("chatContainer");

const clearButton =
    document.getElementById("clearButton");


function addMessage(
    message,
    sender,
    toolUsed = null
) {

    const messageDiv =
        document.createElement("div");


    messageDiv.classList.add(
        "message"
    );


    if (sender === "user") {

        messageDiv.classList.add(
            "user-message"
        );

    } else {

        messageDiv.classList.add(
            "assistant-message"
        );

    }


    const label =
        document.createElement("div");


    label.classList.add(
        "message-label"
    );


    label.textContent =
        sender === "user"
            ? "👤 You"
            : "🤖 AI Agent";


    const text =
        document.createElement("div");


    text.classList.add(
        "message-text"
    );


    text.textContent =
        message;


    messageDiv.appendChild(
        label
    );


    messageDiv.appendChild(
        text
    );


    // Show tool information
    if (
        toolUsed &&
        toolUsed.length > 0
    ) {

        const toolInfo =
            document.createElement("div");


        toolInfo.classList.add(
            "tool-info"
        );


        toolInfo.textContent =
            "🔧 Tool used: " +
            toolUsed.join(", ");


        messageDiv.appendChild(
            toolInfo
        );

    }


    chatContainer.appendChild(
        messageDiv
    );


    chatContainer.scrollTop =
        chatContainer.scrollHeight;

}



async function sendMessage() {

    const message =
        messageInput.value.trim();


    if (!message) {

        return;

    }


    // Add user message
    addMessage(
        message,
        "user"
    );


    // Clear input
    messageInput.value =
        "";


    // Disable button
    sendButton.disabled =
        true;


    // Loading message
    const loadingDiv =
        document.createElement("div");


    loadingDiv.classList.add(
        "message",
        "assistant-message"
    );


    loadingDiv.id =
        "loadingMessage";


    loadingDiv.textContent =
        "🤖 Agent is thinking...";


    chatContainer.appendChild(
        loadingDiv
    );


    chatContainer.scrollTop =
        chatContainer.scrollHeight;


    try {

        const response =
            await fetch(
                "/chat",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            message: message
                        })

                }
            );


        const data =
            await response.json();


        // Remove loading message
        document
            .getElementById(
                "loadingMessage"
            )
            .remove();


        // Add AI response
        addMessage(
            data.response,
            "assistant",
            data.tool_used
        );


    } catch (error) {

        document
            .getElementById(
                "loadingMessage"
            )
            .remove();


        addMessage(
            "Something went wrong. Please try again.",
            "assistant"
        );

    }


    sendButton.disabled =
        false;


    messageInput.focus();

}



sendButton.addEventListener(
    "click",
    sendMessage
);



messageInput.addEventListener(
    "keypress",
    function (event) {

        if (
            event.key === "Enter"
        ) {

            sendMessage();

        }

    }
);



clearButton.addEventListener(
    "click",
    async function () {

        await fetch(
            "/clear",
            {
                method: "POST"
            }
        );


        // Clear UI
        chatContainer.innerHTML =
            "";

    }
);
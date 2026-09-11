async function sendMessage() {

    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    const question = input.value.trim();

    if (question === "") {
        return;
    }

    // Show user message
    const userMessage = document.createElement("div");
    userMessage.className = "message user";
    userMessage.textContent = question;
    chatBox.appendChild(userMessage);

    input.value = "";

    // Show typing animation
    const botMessage = document.createElement("div");
    botMessage.className = "message bot";

    botMessage.innerHTML = `
        <div class="typing">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    chatBox.appendChild(botMessage);

    chatBox.scrollTop = chatBox.scrollHeight;

    try {

        const response = await fetch("http://127.0.0.1:8000/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        if (!response.ok) {
            throw new Error("Server returned an error");
        }

        const data = await response.json();

        // Replace typing animation with answer
        botMessage.textContent = data.answer;

    } catch (error) {

        console.error("Error:", error);

        botMessage.textContent =
            "Sorry, I couldn't connect to the server.";
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}
function clearChat() {

    const chatBox = document.getElementById("chat-box");

    chatBox.innerHTML = `
        <div class="message bot">
            Hello! 👋 How can I help you today?
        </div>
    `;
}


// Press Enter to send
document.getElementById("user-input").addEventListener("keydown", function(event) {

    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }

});
function askSuggestion(question) {
    document.getElementById("user-input").value = question;
    setTimeout(() => {
        sendMessage();
    }, 100);
}
function startFaceRecognition() {
    fetch("/face", {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        alert("Detected mood: " + data.mood);
    });
}

function startVoiceCommand() {
    fetch("/voice", {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("voiceOutput").innerText = "Detected mood: " + data.mood;
    });
}

function submitTextInput() {
    const input = document.getElementById("textInput").value;
    fetch("/text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input })
    })
    .then(response => response.json())
    .then(data => {
        alert("Detected mood: " + data.mood);
    });
}

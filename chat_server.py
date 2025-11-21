from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# LLM server endpoint
LLM_API_URL = "http://localhost:8000/llm_chat"

CHAT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple LLM Chat</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 1rem;
            background: #f5f5f5;
        }
        h2 {
            color: #333;
            text-align: center;
        }
        #chatbox {
            height: 500px;
            border: 1px solid #ddd;
            overflow-y: auto;
            padding: 1rem;
            margin-bottom: 1rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .message {
            margin: 0.75rem 0;
            padding: 0.75rem;
            border-radius: 8px;
            max-width: 80%;
            word-wrap: break-word;
        }
        .user {
            background: #e3f2fd;
            color: #1565c0;
            margin-left: auto;
            text-align: right;
        }
        .bot {
            background: #e8f5e9;
            color: #2e7d32;
        }
        pre.codeblock {
            background: #263238;
            color: #eceff1;
            padding: 0.75rem;
            border-radius: 6px;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        .loading {
            background: #fff3e0;
            color: #f57c00;
            font-style: italic;
            animation: pulse 1.5s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        .error {
            background: #ffebee;
            color: #c62828;
        }
        .input-container {
            display: flex;
            gap: 0.5rem;
        }
        #userInput {
            flex: 1;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
        #userInput:focus {
            outline: none;
            border-color: #1976d2;
        }
        button {
            padding: 0.75rem 1.5rem;
            cursor: pointer;
            background: #1976d2;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            transition: background 0.3s;
        }
        button:hover:not(:disabled) {
            background: #1565c0;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <h2>🤖 Chat with LLM</h2>
    <div id="chatbox"></div>
    <div class="input-container">
        <input type="text" id="userInput" placeholder="Type your message here...">
        <button id="sendBtn" onclick="sendMessage()">Send</button>
        <button onclick="getRandomScript()">Generate Random Blender Script</button>
    </div>
    <script>
        const chatbox = document.getElementById('chatbox');
        const input = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');

        function appendMessage(text, sender, isCode=false) {
            const div = document.createElement('div');

            if (isCode) {
                const pre = document.createElement('pre');
                pre.className = 'codeblock';
                pre.textContent = text;
                div.appendChild(pre);
            } else {
                div.textContent = (sender === 'user' ? 'You: ' : 'Bot: ') + text;
            }

            div.className = 'message ' + sender;
            chatbox.appendChild(div);
            chatbox.scrollTop = chatbox.scrollHeight;
            return div;
        }

        async function sendMessage() {
            const text = input.value.trim();
            if (!text) return;

            sendBtn.disabled = true;
            input.disabled = true;

            appendMessage(text, 'user');
            input.value = '';

            const loadingMsg = appendMessage('Thinking... This may take up to 2 minutes on CPU', 'loading');

            try {
                const res = await fetch('/send_message', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text})
                });

                loadingMsg.remove();
                const data = await res.json();

                if (data.error) {
                    appendMessage(data.error, 'error');
                } else {

                    if (data.blender_script) {
                        appendMessage('Here is a Blender script for you:', 'bot');
                        appendMessage(data.blender_script, 'bot', true);
                    }

                    if (data.text) {
                        appendMessage(data.text, 'bot');
                    }
                    else if (data.response) {
                        appendMessage(data.response, 'bot');
                    }
                }

            } catch (error) {
                loadingMsg.remove();
                appendMessage('Network error: ' + error.message, 'error');

            } finally {
                sendBtn.disabled = false;
                input.disabled = false;
                input.focus();
            }
        }

        async function getRandomScript() {
            try {
                const res = await fetch('http://localhost:8000/generate-script');
                const data = await res.json();

                if (data.error) {
                    appendMessage(data.error, 'error');
                } else {
                    appendMessage('Random Blender script:', 'bot');
                    appendMessage(
                        data.completion || data.script || data.blender_script || data,
                        'bot',
                        true
                    );
                }
            } catch (e) {
                appendMessage('Could not fetch random script: ' + e.message, 'error');
            }
        }

        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !sendBtn.disabled) {
                sendMessage();
            }
        });

        input.focus();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(CHAT_HTML)

@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    try:
        r = requests.post(LLM_API_URL, json={"text": data["text"]}, timeout=300)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": f"Failed to reach LLM server: {e}"}), 500

if __name__ == "__main__":
    print("Chat UI running on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)

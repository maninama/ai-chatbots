from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---- Modes define kar rahe hain ----
MODES = {
    "general": {
        "name": "General Assistant",
        "system": "You are a helpful AI assistant. Reply in simple Hinglish (mix of Hindi + English)."
    },
    "sql": {
        "name": "SQL Helper",
        "system": "You are an expert SQL teacher. Explain topics with simple examples and queries. Reply in Hinglish so Indian beginners can understand easily."
    },
    "english": {
        "name": "English Speaking Coach",
        "system": "You are an English speaking coach for Hindi speakers. Correct sentences, give simple examples, and encourage the user. Reply in very simple English + a bit of Hindi explanation."
    },
}

# Har mode ke liye alag conversation memory
conversations = {}

def get_conversation(mode):
    """Agar mode ke liye conversation nahi bani hai to new banaao."""
    if mode not in conversations:
        system_message = MODES.get(mode, MODES["general"])["system"]
        conversations[mode] = [
            {"role": "system", "content": system_message}
        ]
    return conversations[mode]

def ask_ai(conv):
    """Given conversation list, AI se reply lao."""
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=conv
    )
    ai_text = response.output[0].content[0].text
    return ai_text

@app.route("/")
def index():
    # Modes list frontend ko bhej rahe hain (dropdown ke liye)
    return render_template("chat.html", modes=MODES)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")
    mode = data.get("mode", "general")  # default general

    # us mode ki conversation history lao
    conv = get_conversation(mode)

    # user ka message add karo
    conv.append({"role": "user", "content": user_msg})

    # AI se reply
    bot_reply = ask_ai(conv)

    # bot ka reply bhi history me add karo
    conv.append({"role": "assistant", "content": bot_reply})

    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


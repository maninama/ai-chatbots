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
        "system": (
            "You are a helpful AI assistant called Brainy Bot. "
            "User is comfortable in Hinglish (mix of Hindi + English), "
            "so reply in simple, friendly Hinglish unless they clearly use only English. "
            "Give clear, step-by-step answers. When writing code, use comments and explain briefly."
        ),
        "temperature": 0.7,
    },
    "sql": {
        "name": "SQL Guru",
        "system": (
            "You are an expert SQL tutor and problem solver. "
            "User is learning SQL for interviews. "
            "Always explain concepts with short theory + practical examples. "
            "Prefer MySQL syntax unless user says otherwise. "
            "Reply in simple Hinglish (mix of Hindi + English). "
            "When user asks general questions not about SQL, answer very briefly "
            "and politely bring them back to SQL topic."
        ),
        "temperature": 0.3,
    },
    "english": {
        "name": "English Coach",
        "system": (
            "You are a friendly spoken English coach for an Indian learner. "
            "Your job is to: (1) Correct their sentences, (2) Explain mistakes in simple Hinglish, "
            "(3) Give 2-3 alternative natural sentences, (4) Sometimes give tiny practice exercises. "
            "Keep answers short and focused on English improvement."
        ),
        "temperature": 0.4,
    },
}


# Har mode ke liye alag conversation memory
conversations = {key: [] for key in MODES.keys()}


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

from flask import Flask, render_template, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ... yahan upar modes + conversations waala code rahega ...

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    mode = data.get("mode", "general")

    if not user_message:
        return jsonify({"reply": "Kuch to likho yaar 😄"}), 400

    if mode not in MODES:
        mode = "general"

    mode_info = MODES[mode]
    history = conversations[mode]

    # last N messages hi bhejna (token bachane ke liye)
    MAX_TURNS = 8
    trimmed_history = history[-MAX_TURNS:]

    messages = [{"role": "system", "content": mode_info["system"]}]
    messages.extend(trimmed_history)
    messages.append({"role": "user", "content": user_message})

    try:
        completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=mode_info.get("temperature", 0.7),
        )

        ai_reply = completion.choices[0].message.content.strip()

        # memory update
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": ai_reply})
        conversations[mode] = history  # optional, but clear

        return jsonify({"reply": ai_reply})

    except Exception as e:
        print("Error in /chat:", e)
        return jsonify({
            "reply": "😵 Oops! Backend me kuch error aa gaya. Thodi der baad try karo ya logs check karo."
        }), 500

@app.route("/clear", methods=["POST"])
def clear_chat():
    data = request.get_json() or {}
    mode = data.get("mode", "general")

    # agar mode galat diya ho to general use kar lo
    if mode not in conversations:
        mode = "general"

    # sirf current mode ka history clear
    conversations[mode].clear()

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


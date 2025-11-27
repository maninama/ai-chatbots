from flask import Flask, render_template, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# ---------- OpenAI client ----------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- Modes + memory ----------

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


modes = {
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


# Per-mode memory
conversations = {key: [] for key in modes.keys()}


# ---------- UI ROUTE ----------


conversations = {key: [] for key in modes.keys()}


@app.route("/")
def index():
    return render_template("chat.html", modes=modes)


# ---------- CHAT API ----------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    mode = data.get("mode", "general")

    if not user_message:
        return jsonify({"reply": "Kuch to likho yaar 😄"}), 400

    if mode not in modes:
        mode = "general"

    mode_info = modes[mode]
    history = conversations[mode]


    # last N messages hi bhejna (token save)

    MAX_TURNS = 8
    trimmed_history = history[-MAX_TURNS:]

    messages = [{"role": "system", "content": mode_info["system"]}]
    messages.extend(trimmed_history)
    messages.append({"role": "user", "content": user_message})

    try:
        completion = client.chat.completions.create(
            model="gpt-4.1-mini",  # yahi model tum pehle use kar rahe the
            messages=messages,
            temperature=mode_info.get("temperature", 0.7),
        )

        ai_reply = completion.choices[0].message.content.strip()

        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": ai_reply})
        conversations[mode] = history

        return jsonify({"reply": ai_reply})

    except Exception as e:
        print("Error in /chat:", e)
        return jsonify({
            "reply": "😵 Oops! Backend me kuch error aa gaya. Thodi der baad try karo."
        }), 500



# ---------- CLEAR CHAT API ----------

@app.route("/clear", methods=["POST"])
def clear_chat():
    data = request.get_json() or {}
    mode = data.get("mode", "general")

    if mode not in conversations:
        mode = "general"

    conversations[mode].clear()
    return jsonify({"status": "ok"})


# ---------- MAIN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

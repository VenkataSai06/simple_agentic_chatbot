import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session


load_dotenv()

from agent import run_agent


app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")


# ==========================
# HOME PAGE
# ==========================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==========================
# CHAT API
# ==========================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True) or {}

    user_message = data.get(
        "message",
        ""
    )


    if not user_message.strip():

        return jsonify({
            "error": "Message cannot be empty"
        }), 400


    # Get previous history
    chat_history = session.get(
        "chat_history",
        []
    )


    # Run Agent
    result = run_agent(
        user_message,
        chat_history
    )


    # Save user message
    chat_history.append(
        {
            "role": "user",
            "content": user_message
        }
    )


    # Save assistant response
    chat_history.append(
        {
            "role": "assistant",
            "content": result["response"]
        }
    )


    # Keep last 10 messages
    session["chat_history"] = chat_history[-10:]


    return jsonify({
        "response": result["response"],

        "tool_used": result["tool_used"]
    })


# ==========================
# CLEAR CHAT
# ==========================

@app.route("/clear", methods=["POST"])
def clear_chat():

    session.pop(
        "chat_history",
        None
    )


    return jsonify({
        "message": "Chat cleared successfully"
    })


# ==========================
# RUN APPLICATION
# ==========================

if __name__ == "__main__":

    app.run(
        debug=True
    )
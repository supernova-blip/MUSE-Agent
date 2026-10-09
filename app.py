
from flask import Flask, render_template, request, jsonify
from agent import run_agent

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"reply": "Tell me what you're in the mood for 🎧"})

    try:
        reply = run_agent(message)
        return jsonify({"reply": str(reply)})
    except Exception:
        app.logger.exception("Muse request failed")
        return jsonify({
            "reply": "Oops! Muse couldn't respond. Please try again."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # allows your frontend page (different origin) to call this server

# Set these as real environment variables before running the server —
# never hardcode the token in this file if you plan to share or commit it.
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")


@app.route("/")
def health():
    return "Camera booth backend is running."


@app.route("/send-photo", methods=["POST"])
def send_photo():
    if not BOT_TOKEN or not CHAT_ID:
        return jsonify(ok=False, error="Server is missing BOT_TOKEN or CHAT_ID env vars"), 500

    if "photo" not in request.files:
        return jsonify(ok=False, error="No photo file included in the request"), 400

    photo = request.files["photo"]

    try:
        telegram_resp = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
            data={"chat_id": CHAT_ID},
            files={"photo": (photo.filename or "photo.jpg", photo.stream, photo.mimetype)},
            timeout=15,
        )
        data = telegram_resp.json()
    except requests.RequestException as e:
        return jsonify(ok=False, error=f"Could not reach Telegram: {e}"), 502

    return jsonify(data), telegram_resp.status_code


@app.route("/send-video", methods=["POST"])
def send_video():
    if not BOT_TOKEN or not CHAT_ID:
        return jsonify(ok=False, error="Server is missing BOT_TOKEN or CHAT_ID env vars"), 500

    if "video" not in request.files:
        return jsonify(ok=False, error="No video file included in the request"), 400

    video = request.files["video"]

    try:
        telegram_resp = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
            data={"chat_id": CHAT_ID},
            files={"video": (video.filename or "video.webm", video.stream, video.mimetype)},
            timeout=60,  # videos take longer to upload than photos
        )
        data = telegram_resp.json()
    except requests.RequestException as e:
        return jsonify(ok=False, error=f"Could not reach Telegram: {e}"), 502

    return jsonify(data), telegram_resp.status_code


if __name__ == "__main__":
    # Runs on http://localhost:5000
    app.run(host="0.0.0.0", port=5000, debug=True)

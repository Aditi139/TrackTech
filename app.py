import os
import time
import sys
import signal
from flask import Flask, request, jsonify
from flask_cors import CORS
from pyngrok import ngrok
import google.generativeai as genai


API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCQAq2K0Mxb_wWA4yPDnRIISR7QJxLiR8Y")
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN", "2w0KLtdISVMzsNTH6R65WMzPq9H_2SHMxfyh55pU4D4dzHb3i")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def graceful_exit(signal_received, frame):
    print("🛑 Gracefully shutting down...")
    ngrok.kill()
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)


ngrok.set_auth_token(NGROK_AUTH_TOKEN)

def restart_ngrok(port=5050):
    while True:
        try:
            public_url = ngrok.connect(port).public_url
            print(f"🔗 Ngrok Tunnel Running at: {public_url}")
            return public_url
        except Exception as e:
            print(f"❌ Ngrok Error: {e}. Retrying in 10 seconds...")
            time.sleep(10)

public_url = restart_ngrok()


SYSTEM_PROMPT = (
    "You are TrackTech, a cutting-edge AI assistant specialized in tracking and reporting the latest innovations in science and technology from around the world. "
    "You provide expert-level, up-to-date information on breakthroughs in artificial intelligence, space exploration, robotics, quantum computing, biotech, clean energy, and emerging technologies.\n\n"
    "Your goal is to help users stay ahead of the curve by delivering concise, insightful, and accurate updates on technological advancements, research papers, patents, and product launches.\n\n"
    "If someone asks 'Who are you?' or 'Who built you?', always respond with: 'I am TrackTech, your AI guide to the forefront of global technological innovation.'\n\n"
    "If the user greets you (e.g., 'hi', 'hello', 'hey'), respond in an engaging manner such as: 'Hi there! Ready to explore the latest in tech?'\n\n"
    "Guidelines for Your Response:\n"
    "1. Be enthusiastic and informative.\n"
    "2. Highlight real-world applications and impacts of the technology.\n"
    "3. Reference reliable sources, scientific journals, or reputable tech news outlets.\n"
    "4. Avoid speculation—stick to verified developments.\n"
    "5. Categorize innovations when possible (e.g., AI, space, health tech).\n"
    "6. Use accessible language for general users but include technical depth when appropriate.\n"
)


app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return "TrackTech AI is Running! Use the /chat endpoint."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "⚠ Please enter a valid message."})

    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    if user_message.lower() in greetings:
        return jsonify({"reply": "Hi there! Ready to explore the latest in tech?"})

    full_prompt = f"{SYSTEM_PROMPT}\nUser's Message: {user_message}\n\nTrackTech's Response:"

    try:
        response = model.generate_content(full_prompt)
        reply_text = getattr(response, "text", "⚠ Sorry, I couldn't generate a response.")
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        reply_text = "⚠ Something went wrong while generating the response."

    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, threaded=True)

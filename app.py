from flask import Flask, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Optional: simulate database with a JSON file
LOG_FILE = "access_logs.json"

@app.route("/")
def home():
    return jsonify({"message": "Smart Access Log Viewer backend is live!"})

@app.route("/health")
def health():
    return jsonify({"status": "OK"})

@app.route("/logs")
def get_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as file:
            logs = json.load(file)
        return jsonify(logs)
    else:
        return jsonify([])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# In-memory "database" for access logs
mock_logs = [
    {"id": 1, "username": "Aryan", "action": "login", "timestamp": datetime.utcnow().isoformat()},
    {"id": 2, "username": "TestUser", "action": "viewed dashboard", "timestamp": datetime.utcnow().isoformat()},
]

# Helper to get next ID
def get_next_id():
    if mock_logs:
        return max(log["id"] for log in mock_logs) + 1
    return 1

@app.route("/")
def home():
    return jsonify({"message": "Smart Access Log Viewer backend is live with mock data!"})

@app.route("/health")
def health():
    return jsonify({"status": "OK", "db_connection": "Mock DB active"})

# CREATE - Insert a new log
@app.route("/logs", methods=["POST"])
def create_log():
    data = request.get_json()
    username = data.get("username")
    action = data.get("action")

    if not username or not action:
        return jsonify({"error": "username and action are required"}), 400

    new_log = {
        "id": get_next_id(),
        "username": username,
        "action": action,
        "timestamp": datetime.utcnow().isoformat()
    }
    mock_logs.append(new_log)
    return jsonify({"message": "Log created successfully", "id": new_log["id"]}), 201

# READ - Get all logs
@app.route("/logs", methods=["GET"])
def get_logs():
    # Return logs ordered by timestamp descending
    sorted_logs = sorted(mock_logs, key=lambda x: x["timestamp"], reverse=True)
    return jsonify(sorted_logs)

# UPDATE - Update a log entry
@app.route("/logs/<int:log_id>", methods=["PUT"])
def update_log(log_id):
    data = request.get_json()
    action = data.get("action")

    if not action:
        return jsonify({"error": "action is required"}), 400

    for log in mock_logs:
        if log["id"] == log_id:
            log["action"] = action
            return jsonify({"message": "Log updated successfully"})
    return jsonify({"error": "Log not found"}), 404

# DELETE - Delete a log entry
@app.route("/logs/<int:log_id>", methods=["DELETE"])
def delete_log(log_id):
    global mock_logs
    new_logs = [log for log in mock_logs if log["id"] != log_id]
    if len(new_logs) == len(mock_logs):
        return jsonify({"error": "Log not found"}), 404
    mock_logs = new_logs
    return jsonify({"message": "Log deleted successfully"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# Database connection info from environment variables
DB_HOST = os.getenv("DB_HOST", "your-db-endpoint.rds.amazonaws.com")
DB_NAME = os.getenv("DB_NAME", "yourdbname")
DB_USER = os.getenv("DB_USER", "yourdbuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "yourdbpassword")
DB_PORT = os.getenv("DB_PORT", "5432")


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )


# Ensure the table exists
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS access_logs (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database table 'access_logs' is ready.")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")


@app.route("/")
def home():
    return jsonify({"message": "Smart Access Log Viewer backend is live with RDS!"})


@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        return jsonify({"status": "OK", "db_connection": "Success"})
    except Exception as e:
        return jsonify({"status": "ERROR", "db_connection": str(e)}), 500


# CREATE - Insert a new log
@app.route("/logs", methods=["POST"])
def create_log():
    try:
        data = request.get_json()
        username = data.get("username")
        action = data.get("action")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO access_logs (username, action) VALUES (%s, %s) RETURNING id;",
            (username, action)
        )
        log_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Log created successfully", "id": log_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# READ - Get all logs
@app.route("/logs", methods=["GET"])
def get_logs():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM access_logs ORDER BY timestamp DESC;")
        rows = cur.fetchall()
        logs = [
            {"id": row[0], "username": row[1], "action": row[2], "timestamp": row[3].isoformat()}
            for row in rows
        ]
        cur.close()
        conn.close()
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# UPDATE - Update a log entry
@app.route("/logs/<int:log_id>", methods=["PUT"])
def update_log(log_id):
    try:
        data = request.get_json()
        action = data.get("action")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE access_logs SET action = %s WHERE id = %s;", (action, log_id))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Log updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# DELETE - Delete a log entry
@app.route("/logs/<int:log_id>", methods=["DELETE"])
def delete_log(log_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM access_logs WHERE id = %s;", (log_id,))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Log deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    init_db()  # Ensure DB is ready before serving requests
    app.run(host="0.0.0.0", port=5000)

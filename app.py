from flask import Flask, jsonify
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

@app.route("/")
def home():
    return jsonify({"message": "Smart Access Log Viewer backend is live with RDS!"})

@app.route("/health")
def health():
    return jsonify({"status": "OK"})

@app.route("/logs")
def get_logs():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM access_logs ORDER BY timestamp DESC;")
        rows = cur.fetchall()

        # Convert rows to dictionaries
        logs = [
            {
                "id": row[0],
                "username": row[1],
                "action": row[2],
                "timestamp": row[3].isoformat()
            }
            for row in rows
        ]

        cur.close()
        conn.close()

        return jsonify(logs)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

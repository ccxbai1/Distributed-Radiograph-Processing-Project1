import os
import json
import time
from flask import Flask, jsonify, request
from kafka import KafkaProducer
import psycopg2

# ---------- Config from environment variables ----------
BOOTSTRAP = os.environ["KAFKA_BOOTSTRAP"]              # comma-separated host:port list
TOPIC = os.environ.get("KAFKA_TOPIC", "rfo-jobs")

SCRAM_USER = os.environ["KAFKA_USER"]
SCRAM_PASS = os.environ["KAFKA_PASS"]

DB_HOST = os.environ["DB_HOST"]                        # RDS endpoint (no port)
DB_NAME = os.environ.get("DB_NAME", "rfoapp")
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
DB_PORT = int(os.environ.get("DB_PORT", "5432"))

API_PORT = int(os.environ.get("API_PORT", "8000"))

# ---------- Helpers ----------
def db_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        connect_timeout=10
    )

producer = KafkaProducer(
    bootstrap_servers=[s.strip() for s in BOOTSTRAP.split(",") if s.strip()],
    security_protocol="SASL_SSL",
    sasl_mechanism="SCRAM-SHA-512",
    sasl_plain_username=SCRAM_USER,
    sasl_plain_password=SCRAM_PASS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    retries=3
)

app = Flask(__name__)

# ---------- Routes ----------
@app.get("/health")
def health():
    return jsonify({"ok": True, "topic": TOPIC})

@app.post("/submit")
def submit():
    """
    Body: {"image_key":"somefile.png"}
    Enqueues Kafka message: {"image_key": "...", "ts": ...}
    """
    data = request.get_json(force=True, silent=False)
    if not data or "image_key" not in data:
        return jsonify({"error": "Missing required field: image_key"}), 400

    image_key = data["image_key"].strip()
    if not image_key:
        return jsonify({"error": "image_key cannot be empty"}), 400

    msg = {"image_key": image_key, "ts": time.time()}

    producer.send(TOPIC, msg)
    producer.flush()

    return jsonify({"queued": True, "topic": TOPIC, "image_key": image_key})

@app.get("/recent")
def recent():
    """
    Query: /recent?n=10
    Returns most recent jobs from RDS.
    """
    try:
        n = int(request.args.get("n", "10"))
    except ValueError:
        return jsonify({"error": "n must be an integer"}), 400

    n = max(1, min(n, 100))  # clamp 1..100

    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT created_at, image_key, overlay_key, status, box
                FROM jobs
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (n,)
            )
            rows = cur.fetchall()

    result = []
    for created_at, image_key, overlay_key, status, box in rows:
        result.append({
            "created_at": created_at.isoformat(),
            "image_key": image_key,
            "overlay_key": overlay_key,
            "status": status,
            "box": box
        })

    return jsonify(result)

# ---------- Main ----------
if __name__ == "__main__":
    # Run on all interfaces so it can be reached via instance IP (if you later allow it)
    app.run(host="0.0.0.0", port=API_PORT)
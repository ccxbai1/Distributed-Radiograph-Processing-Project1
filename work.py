import os, json, time, random
from kafka import KafkaConsumer
import boto3
from PIL import Image, ImageDraw
import psycopg2

BOOTSTRAP = os.environ["KAFKA_BOOTSTRAP"]
TOPIC = "rfo-jobs"

S3_INPUT_BUCKET = os.environ["S3_INPUT_BUCKET"]
S3_OUTPUT_BUCKET = os.environ["S3_OUTPUT_BUCKET"]

DB_HOST = os.environ["DB_HOST"]
DB_NAME = os.environ.get("DB_NAME", "rfoapp")
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]

SCRAM_USER = os.environ["KAFKA_USER"]
SCRAM_PASS = os.environ["KAFKA_PASS"]

s3 = boto3.client("s3")

def db_conn():
    return psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS, connect_timeout=10
    )

def make_overlay(local_in, local_out):
    img = Image.open(local_in).convert("RGB")
    w, h = img.size

    # random box, keep it inside image
    x1 = random.randint(0, max(0, w - 50))
    y1 = random.randint(0, max(0, h - 50))
    x2 = random.randint(x1 + 20, min(w, x1 + max(30, w // 3)))
    y2 = random.randint(y1 + 20, min(h, y1 + max(30, h // 3)))

    draw = ImageDraw.Draw(img)
    draw.rectangle([x1, y1, x2, y2], outline=(255, 0, 0), width=4)

    img.save(local_out, format="PNG")
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP.split(","),
    security_protocol="SASL_SSL",
    sasl_mechanism="SCRAM-SHA-512",
    sasl_plain_username=SCRAM_USER,
    sasl_plain_password=SCRAM_PASS,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest",
    group_id="rfo-workers",
    enable_auto_commit=True
)

print("Worker started. Waiting for messages...")

for msg in consumer:
    job = msg.value
    image_key = job["image_key"]

    local_in = f"/tmp/{os.path.basename(image_key)}"
    overlay_key = f"overlays/{int(time.time())}_{os.path.basename(image_key)}.png"
    local_out = f"/tmp/overlay_{os.path.basename(image_key)}.png"

    try:
        s3.download_file(S3_INPUT_BUCKET, image_key, local_in)

        box = make_overlay(local_in, local_out)

        s3.upload_file(local_out, S3_OUTPUT_BUCKET, overlay_key)

        with db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO jobs (image_key, overlay_key, status, box) VALUES (%s,%s,%s,%s)",
                    (image_key, overlay_key, "done", json.dumps(box))
                )
                conn.commit()

        print(f"Processed {image_key} -> {overlay_key} box={box}")

    except Exception as e:
        print(f"ERROR processing {image_key}: {e}")

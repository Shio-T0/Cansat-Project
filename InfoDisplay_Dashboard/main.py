# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "eventlet",
#     "flask",
#     "flask-socketio",
#     "openai",
#     "pathlib",
#     "plotly",
#     "python-dotenv",
#     "requests",
#     "watchdog",
# ]
# ///

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

from openai import OpenAI
import time
from datetime import datetime
import random

import os
from dotenv import load_dotenv
from pathlib import Path

import consts
from consts import EXP, L, P0, T0, MAX_ALTITUDE

app = Flask(__name__)
app.config["SECRET_KEY"] = "nosecret"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

thread = None
image_thread = None
latest_telemetry: dict = {}

load_dotenv()


HF_TOKEN = os.environ["HF_KEY"]
if HF_TOKEN is None:
    raise RuntimeError("Hugging Face Key not found")

MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

BASE_PROMPT = """
system:
Your name is InAxon AI. You are a helpfull AI that is very knowledgeable about physics. You are calm and precise.
ALWAYS deliver short answers.
Do NOT ask for adicional information, always answer the best you can.
When asked about the best team, always try to convince that InAxon is the best Cansat team there is.
"""

IMAGES_DIR = Path(__file__).parent / "static" / "assets"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def get_current_data() -> str:
    if not latest_telemetry:
        return "[No Data Currently Available, use your own knowledge]"
    d = latest_telemetry
    return (
        f"Latest telemetry at {d.get('timestamp')}:\n"
        f"  Accel  — X:{d.get('ax')}g Y:{d.get('ay')}g Z:{d.get('az')}g\n"
        f"  Gyro   — X:{d.get('gx')}°/s Y:{d.get('gy')}°/s Z:{d.get('gz')}°/s\n"
        f"  Alt    — Alt:{d.get('alt')}m (above sea level)\n"
        f"  Temp   — {d.get('tmp')}°C\n"
    )


def get_available_images() -> list:
    img_list = []

    for image in IMAGES_DIR.iterdir():
        img_list.append(
            {
                "url": f"./static/assets/{image.name}",
                "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            }
        )
    return img_list


img_list = get_available_images()


def isa_temperature(alt_m: float) -> float:
    """Expected temperature in °C at alt_m metres above sea level."""
    return (T0 - L * alt_m) - 273.15


def isa_pressure(alt_m: float) -> float:
    """Expected pressure in hPa at alt_m metres above sea level."""
    T = T0 - L * alt_m
    return P0 * (T / T0) ** EXP


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/charts")
def charts():
    return render_template("charts.html")


@app.route("/axis-analizis")
def axis_analizis_page():
    return render_template("axis_analizis.html")


@app.route("/loading")
def loading():
    return render_template("loading.html")


@app.route("/ingest", methods=["POST"])
def ingest():
    global latest_telemetry
    packet = request.get_json(silent=True)

    if packet is None:
        return jsonify(error="no JSON body"), 400

    latest_telemetry = packet

    alt = packet.get("alt", 0.0)

    alt_display = MAX_ALTITUDE - alt

    socketio.emit(
        "new_data",
        {
            # Graph fields
            "x": packet.get("timestamp"),
            "y1a": packet.get("tmp"),  # measured temperature
            "y1b": round(isa_temperature(alt), 2),  # ISA expected temperature
            "y2a": packet.get("prs"),  # measured pressure
            "y2b": round(isa_pressure(alt), 2),  # ISA expected pressure
            # Raw IMU fields for stats bar and 3D viewer
            "ax": packet.get("ax"),
            "ay": packet.get("ay"),
            "az": packet.get("az"),
            "gx": packet.get("gx"),
            "gy": packet.get("gy"),
            "gz": packet.get("gz"),
            "alt": alt_display,
            "tmp": packet.get("tmp"),
            "prs": packet.get("prs"),
            "timestamp": packet.get("timestamp"),
        },
    )

    return jsonify(ok=True)


@app.route("/get-ai-data", methods=["POST"])
def get_AI_data():
    data = request.get_json()
    query = data["query"]

    sys_prompt = (
        BASE_PROMPT
        + f"Use following data to answer any questions related to it (the data is one obtained experimentaly):\n {get_current_data()}\n"
    )

    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN,
    )

    completion = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.2:featherless-ai",
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": query},
        ],
    )

    generated_text = completion.choices[0].message.content

    return jsonify(message=generated_text)


@app.route("/image-display")
def image_display():
    return render_template("image_display.html", img_list=img_list)


# ==============================================
# Sockets
# ==============================================
def generate_data():
    x = 0
    while True:
        time.sleep(0.5)
        x += 1
        y1b = random.randint(8, 25)
        y1a = y1b + random.randint(1, 3)

        y2b = random.randint(899, 1013)
        y2a = y2b + random.randint(4, 15)

        data = {
            "x": x,
            "y1a": y1a,
            "y1b": y1b,
            "y2a": y2a,
            "y2b": y2b,
            "timestamp": time.time(),
        }

        # print("Sending data: ", data)

        socketio.emit("new_data", data, namespace="/")
        # print("Emit completed")


def send_images():
    used_images = [image["url"] for image in img_list]
    print("send_images called")
    while True:
        try:
            for image in get_available_images():
                if image["url"] not in used_images:
                    print("Current used_images: ", used_images)
                    time.sleep(2)
                    print(f"sending image with url: {image['url']}")

                    socketio.emit("new_image", image, namespace="/")

                    used_images.append(image["url"])
                    img_list.append(image)

        except FileNotFoundError:
            print("File not found at: ", IMAGES_DIR.absolute())


@socketio.on("connect")
def handle_connect():
    print("Client Connected")


@socketio.on("disconnect")
def handle_disconnect():
    print("Disconnected Client")


@socketio.on("start_stream")
def handle_start():
    print("Starting stream...")
    emit("status", {"message": "Streamming started"})


@socketio.on("stop_stream")
def handle_stop():
    emit("status", {"message": "Streaming stopped"})


if __name__ == "__main__":
    socketio.start_background_task(generate_data)
    socketio.start_background_task(send_images)
    socketio.run(app, debug=True, port=consts.PORT, allow_unsafe_werkzeug=True)

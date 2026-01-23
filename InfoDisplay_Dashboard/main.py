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
# ]
# ///

from flask import Flask, render_template, jsonify, request, url_for
from flask_socketio import SocketIO, emit

from threading import Thread, Event
from openai import OpenAI
import time
from datetime import datetime
import random

import os
from dotenv import load_dotenv
from pathlib import Path




app = Flask(__name__)
app.config['SECRET_KEY'] = 'nosecret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=True, engineio_logger=True)

thread = None
image_thread = None
thread_stop_event = Event()
image_thread_stop_event = Event()

load_dotenv()


# =======
# Consts
# =======
HF_TOKEN = os.environ["HF_KEY"]
if HF_TOKEN is None:
    raise RuntimeError("Hugging Face Key not found")

MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

BASE_PROMPT = """
system:
Your name is InAxon. You are a helpfull AI that is very knowledgeable about physics. You are calm and precise.
ALWAYS deliver short answers.
Do NOT ask for adicional information, always answer the best you can.
"""

ASSETS = Path("./assets")

def get_current_data():
    return "[No Data Currently Available, use your own knowledge]"



@app.route("/")
def index():
    return render_template('index.html')
    

@app.route("/charts")
def charts():
    return render_template("charts.html")

@app.route("/axis-analizis")
def axis_analizis_page():
    return render_template('axis_analizis.html')


@app.route("/loading")
def loading():
    return render_template('loading.html')


@app.route("/get-ai-data", methods=["POST"])
def get_AI_data():
    data = request.get_json()
    query = data["query"]
    
    sys_prompt = BASE_PROMPT + f"Use following data to answer any questions related to it (the data is one obtained experimentaly):\n {get_current_data()}\n"

    
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN,
    )

    completion = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.2:featherless-ai",
        messages=[
            {
                "role": "system",
                "content": sys_prompt
            },
            {
                "role": "user",
                "content": query
            }
        ],
    )

    generated_text = completion.choices[0].message.content

    return jsonify(message=generated_text)


@app.route("/image-display")
def image_display():
    return render_template('image_display.html')



# ==============================================
# Sockets
# ==============================================
def generate_data():
    x = 0
    while not thread_stop_event.is_set():
        time.sleep(0.5)
        x += 1
        y1b = random.randint(8, 25)
        y1a = y1b + random.randint(1, 3)

        y2b = random.randint(899, 1013)
        y2a = y2b + random.randint(4,15)

        data = {
            "x": x,
            "y1a": y1a,
            "y1b": y1b,
            "y2a": y2a,
            "y2b": y2b,
            'timestamp': time.time()
        }

        # print("Sending data: ", data)

        socketio.emit("new_data", data, namespace="/")
        # print("Emit completed")

# TODO: Implement this:
def send_images():
    used_images = []
    print("send_images called")
    while not image_thread_stop_event.is_set():

        for image in ASSETS.iterdir():
            if image not in used_images:
                time.sleep(2)
                print("sending image: ", image)

                socketio.emit("new_image", {
                    "url": url_for('assets', filename=image.name),
                    "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3]
                }, namespace="/")
                used_images.append(image)

@socketio.on("connect")
def handle_connect():
    global thread
    global image_thread
    print("Client Connected")

    if thread is None or not thread.is_alive():
        thread_stop_event.clear()
        thread = Thread(target=generate_data)
        thread.daemon = True
        thread.start()
    
    if image_thread is None or not image_thread.is_alive():
        print("starting image_thread")
        image_thread_stop_event.clear()
        image_thread = Thread(target=send_images)
        image_thread.daemon = True
        image_thread.start()

@socketio.on("disconnect")
def handle_disconnect():
    print("Disconnected Client")

@socketio.on("start_stream")
def handle_start():
    print("Starting stream...")
    emit('status', {'message': 'Streamming started'})


@socketio.on("stop_stream")
def handle_stop():
    thread_stop_event.set()
    emit('status', {'message': 'Streaming stopped'})


if __name__ == "__main__":
    socketio.run(app, debug=True)

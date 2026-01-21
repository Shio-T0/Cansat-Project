# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "eventlet",
#     "flask",
#     "flask-socketio",
#     "openai",
#     "plotly",
#     "python-dotenv",
#     "requests",
# ]
# ///
COLOR_LIST = [
    '#00FFF2',
    '#4F86C6',
    '#5100FF',
    '#1294FF'
]

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

from threading import Thread, Event
import requests
from openai import OpenAI
import time
import random

import os
from dotenv import load_dotenv

import plotly.graph_objs as go
import plotly.offline as pyo


app = Flask(__name__)
app.config['SECRET_KEY'] = 'nosecret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=True, engineio_logger=True)

thread = None
thread_stop_event = Event()

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

# ===========
# Sockets
# ===========
def generate_data():
    x = 0
    while not thread_stop_event.is_set():
        time.sleep(0.5)
        x += 1
        y1a = random.randint(1, 50)
        y1b = random.randint(1, 50)
        y2a = random.randint(1, 50)
        y2b = random.randint(1, 50)

        data = {
            "x": x,
            "y1a": y1a,
            "y1b": y1b,
            "y2a": y2a,
            "y2b": y2b,
            'timestamp': time.time()
        }

        print("Sending data: ", data)

        socketio.emit("new_data", data, namespace="/")
        print("Emit completed")


@socketio.on("connect")
def handle_connect():
    global thread
    print("Client Connected")

    if thread is None or not thread.is_alive():
        thread_stop_event.clear()
        thread = Thread(target=generate_data)
        thread.daemon = True
        print("Starting thread")
        thread.start()

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

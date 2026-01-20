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
from flask_socketio import SocketIO

import threading
import requests
from openai import OpenAI
import time
import random

import os
from dotenv import load_dotenv

import plotly.graph_objs as go
import plotly.offline as pyo


app = Flask(__name__)
socketio = SocketIO(app, async_mode="eventlet")

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

def generate_data():
    x = 0
    while True:
        time.sleep(2)
        x += 1
        y = random.random()

        socketio.emit("new_data", {
            "x": x,
            "y": y
        })

    
    threading.Thread(target=generate_data, daemon=True).start()


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


if __name__ == "__main__":
    socketio.run(app, debug=True)

# /// script
# requires-python = ">=3.13"
# dependencies = [
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
import requests
from openai import OpenAI

import os
from dotenv import load_dotenv

import plotly.graph_objs as go
import plotly.offline as pyo


app = Flask(__name__)

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

def buildScatterFigure(x: list, y: list) -> object:
    """
    Creates a plotly Scatter figure
    
    Args:
        x (list): x axis.
        y (list): y axis.

    Returns:
        object: Plotly Scatter Figure
    """

    fig = go.Figure(
        data=[
            go.Scatter(
                x=x,
                y=y,
                line=dict(shape='linear', color='rgba(36, 255, 255, 0.678)'),
                mode='lines+markers'
            )
        ]
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(20, 20, 20, 0.5)',
        margin=dict(l=0, r=0, t=0, b=0),
        autosize=True,
        xaxis=dict(
            linecolor='rgba(40,40,40,1)'
        ),
        yaxis=dict(
            linecolor='rgba(40,40,40,1)'
        ),
        font=dict(color=COLOR_LIST[3]),
        height=240,
        width=460
    )
    fig.update_yaxes(
        gridcolor='rgba(40,40,40,1)'
    )
    fig.update_xaxes(
        gridcolor='rgba(40,40,40,1)'
    )

    # Making Pyo plot
    graph_div = fig.to_html(
        full_html=False, 
        include_plotlyjs="cdn", 
        config={'displayModeBar': False,
                'responsive': True}
    )
    
    return graph_div


@app.route("/")
def index():
    return render_template('index.html')
    

@app.route("/charts")
def charts():
    scatter_a1 = buildScatterFigure(
        x=[1,2,3,4,5],
        y=[1,3,4,4,1]
    )
    scatter_a2 = buildScatterFigure(
        x=[1,2,3,4,5],
        y=[1,3,4,4,1]
    )
    scatter_b1 = buildScatterFigure(
        x=[1,2,3,4,5],
        y=[1,3,4,4,1]
    )
    scatter_b2 = buildScatterFigure(
        x=[1,2,3,4,5],
        y=[1,3,4,4,1]
    )
    return render_template(
        "charts.html",
        scatter_a1=scatter_a1,
        scatter_a2=scatter_a2,
        scatter_b1=scatter_b1,
        scatter_b2=scatter_b2,
    )

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
    app.run(debug=True)

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "datetime",
#     "eventlet",
#     "flask",
#     "flask-socketio",
#     "pandas",
#     "plotly",
#     "requests",
# ]
# ///
COLOR_LIST = [
    '#00FFF2',
    '#4F86C6',
    '#5100FF',
    '#1294FF'
]

from flask import Flask, render_template, jsonify

import plotly.graph_objs as go
import plotly.offline as pyo


app = Flask(__name__)


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
        height=200
    )
    fig.update_yaxes(
        gridcolor='rgba(40,40,40,1)'
    )
    fig.update_xaxes(
        gridcolor='rgba(40,40,40,1)'
    )

    # Making Pyo plot
    graph_div = pyo.plot(fig, 
        include_plotlyjs=False, 
        output_type='div',
        config={'displayModeBar': False,
                'responsive': True}
    )
    
    return graph_div


@app.route("/")
def index():
    return render_template('index.html')
    

@app.route("/charts")
def charts():
    scatter1 = buildScatterFigure(
        x=[1,2,3,4,5],
        y=[1,3,4,4,1]
    )

    return render_template(
        "charts.html",
        scatter1=scatter1,
    )

@app.route("/axis-analizis")
def axis_analizis_page():
    return render_template('axis_analizis.html')


if __name__ == "__main__":
    app.run(debug=True)

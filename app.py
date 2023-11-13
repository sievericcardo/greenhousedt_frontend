from flask import Flask, render_template
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from io import BytesIO
import base64

app = Flask(__name__)

@app.route('/')
def index():
    # Generate Matplotlib graph
    graph_data = generate_matplotlib_graph()

    # Pass data to the template
    text_content = "This is some text content."

    return render_template('index.html', text_content=text_content, graph_data=graph_data)

def generate_matplotlib_graph():
    # Your Matplotlib graph generation logic goes here
    # For demonstration purposes, let's create a simple plot
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8, 10]

    matplotlib.use('agg')

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_title('Matplotlib Graph')

    # Save the plot to a BytesIO object
    buffer = BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buffer)
    buffer.seek(0)
    plt.close(fig)

    # Convert the BytesIO object to a base64-encoded string
    graph_data = base64.b64encode(buffer.read()).decode('utf-8')

    return graph_data

@app.after_request
def clean_up(response):
    # Clear Matplotlib figure after each request
    plt.clf()
    plt.close('all')
    return response

@app.after_request
def clean_up(response):
    # Clear Matplotlib figure after each request
    plt.clf()
    plt.close('all')
    return response

if __name__ == '__main__':
    app.run(debug=True)
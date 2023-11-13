from flask import Flask, render_template, jsonify
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import requests
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

@app.route('/submit', methods=['POST'])
def submit():
    # Get data from the form
    query = "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
            PREFIX ast: <http://www.semanticweb.org/gianl/ontologies/2023/1/sirius-greenhouse#> \
            PREFIX owl: <http://www.w3.org/2002/07/owl#> \
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> \
            INSERT { \
            ast:basilicum3 rdf:type owl:NamedIndividual , \
                                    ast:Basilicum ; \
                        ast:hasIdealMoisture \"60.0\"^^xsd:double ; \
                        ast:hasPlantId \"5\"^^xsd:string . \
            } \
            WHERE { \
            FILTER NOT EXISTS { ast:basilicum3 rdf:type ast:Basilicum . \
            } \
            } "
    
    data = {'update': query}
    # make a post request to http://localhost:3030/GreenHouse/update
    r = requests.post('http://localhost:3030/GreenHouse/update', data=data)

    # Process the data if needed
    result = f"Query submitted: {query}"

    # Return a JSON response
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
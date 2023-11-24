from flask import Flask, render_template, jsonify
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import requests
from io import BytesIO
import base64
import json
import pandas as pd
import matplotlib.dates as mdates

app = Flask(__name__)

@app.route('/')
def index():
    # Generate Matplotlib graph
    graph_data = __generate_matplotlib_graph()

    # Pass data to the template
    text_content = "This is some text content."

    return render_template('index.html', text_content=text_content, graph_data=graph_data)

@app.route('/get_model')
def get_model():
    return __get_model()

def __get_model ():
    delimiters = ["Plant", "Pot", "Pump"]
    models = {}
    
    with open('model.txt', 'r') as file:
        model = file.read()

    for delimiter in delimiters:
        start = model.find(f"RECONFIG> New {delimiter}(s) detected: repairing the model")
        end = model.find(f"RECONFIG> {delimiter}(s) added")

        if start != -1 and end != -1:
            models[delimiter] = model[start:end]

    return json.dumps(models)

@app.route('/get_graph')
def get_graph():
    graph_data = __generate_matplotlib_graph()
    return {'graph_data': graph_data}

def __generate_matplotlib_graph():
    df = pd.read_csv('query.csv')

    df_m = df.loc[df['_field'] == 'moisture', :]

    # Remove rows with invalid '_time' values using regular expressions
    df_m = df_m[df_m['_time'].str.contains('\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', na=False)]

    # Convert the date column to a datetime format and rename to 'ds', and the target column to 'y'
    df_m['ds'] = pd.to_datetime(df_m['_time'], errors='coerce').dt.tz_convert(None)

    df_m.dropna(subset=['ds'], inplace=True)

    # Filter out the rows with invalid target values using regular expressions
    df_m = df_m[~df_m['_value'].str.contains('[^0-9\.]', na=False)]

    # Convert the target column to numeric format
    df_m['y'] = pd.to_numeric(df_m['_value'])

    # Check for out-of-range date values
    out_of_range_dates = df_m[(df_m['ds'] < pd.Timestamp('0001-01-01')) | (df_m['ds'] > pd.Timestamp('9999-12-31'))]

    # Set figure and axis using subplots()
    matplotlib.use('agg')
    fig, ax = plt.subplots()

    # Plot the data
    df_m.plot(x='ds', y='y', kind='line', ax=ax, x_compat=True)

    # Set the x-axis label
    ax.set_xlabel('Date')
    ax.set_ylabel('Moisture %')

    # Format the x-axis ticks (display month and day without year)
    date_fmt = mdates.DateFormatter('%d %b')
    ax.xaxis.set_major_formatter(date_fmt)
    ax.set_title('Moisture over time')

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
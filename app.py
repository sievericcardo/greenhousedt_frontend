from flask import Flask, render_template, jsonify, request
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import requests
from io import BytesIO
import base64
import json
import pandas as pd
import matplotlib.dates as mdates
import stomp
import os
import time
from influxdb_client import InfluxDBClient, QueryApi

# Create a connection listener to handle callbacks from the STOMP connection
class StompConnectionListener(stomp.ConnectionListener):
    def on_error(self, headers, message):
        print(f'Received an error: {message}')

    def on_message(self, headers, body):
        print(f'Received message: {body}')

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

def __get_model():
    delimiters = ["Plant", "Pot", "Pump"]
    models = {delimiter: {'added': '', 'changed': '', 'removed': ''} for delimiter in delimiters}

    with open('model.txt', 'r') as file:
        model = file.read()

    for delimiter in delimiters:
        # Find added
        start = model.rfind(f"RECONFIG> New {delimiter}(s) detected: repairing the model")
        end = model.rfind(f"RECONFIG> {delimiter}(s) added")
        if start != -1 and end != -1:
            models[delimiter]['added'] = model[start:end]

        # Find changed
        start = model.rfind(f"RECONFIG> Changed {delimiter}(s) detected: repairing the model")
        end = model.rfind(f"RECONFIG> {delimiter}(s) changed")
        if start != -1 and end != -1:
            models[delimiter]['changed'] = model[start:end]

        # Find removed
        start = model.rfind(f"RECONFIG> Misconfigured {delimiter}(s) detected: repairing the model")
        end = model.rfind(f"RECONFIG> {delimiter}(s) removed")
        if start != -1 and end != -1:
            models[delimiter]['removed'] = model[start:end]

    return json.dumps(models)

@app.route('/get_graph')
def get_graph():
    graph_data = __generate_matplotlib_graph()
    return {'graph_data': graph_data}

def __generate_matplotlib_graph():
    __load_env_file()

    mode = os.getenv("MODE")
    
    # Your InfluxDB credentials and information
    influxdb_url = os.getenv("INFLUXDB_URL")
    org = os.getenv("INFLUXDB_ORG")
    token = os.getenv("INFLUXDB_TOKEN_" + mode.upper())

    bucket = os.getenv("INFLUXDB_BUCKET_" + mode.upper())
    measurement = "ast:pot"
    field = "moisture"

    print(f"Using {mode} mode")
    print(f"Using bucket {bucket}")
    print(f"Using measurement {measurement}")
    print(f"Using field {field}")
    print(f"Using InfluxDB URL {influxdb_url}")
    print(f"Using InfluxDB org {org}")
    print(f"Using InfluxDB token {token}")

    # Initialize the client
    client = InfluxDBClient(url=influxdb_url, token=token, org=org)

    # Initialize the query API
    query_api = client.query_api()

    if mode == "demo":
        flux_query = f'''
        from(bucket: "{bucket}")
            |> range(start: 2023-11-12T00:00:00Z, stop: 2023-12-03T00:00:00Z)
            |> filter(fn: (r) => r._measurement == "{measurement}")
            |> filter(fn: (r) => r._field == "{field}")
            |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
            |> yield(name: "mean")
        '''
    else:
        flux_query = f'''
        from(bucket: "{bucket}")
            |> range(start: -20d)
            |> filter(fn: (r) => r._measurement == "{measurement}")
            |> filter(fn: (r) => r._field == "{field}")
            |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
            |> yield(name: "mean")
        '''

    # Execute the query
    result = query_api.query(query=flux_query)

    # Extract relevant data from the result
    flux_table = result[0]

    # Extract _time and _value columns
    timestamps = [point['_time'] for point in flux_table.records]
    values = [point['_value'] for point in flux_table.records]

    # Convert _time to numeric format
    timestamps_numeric = mdates.date2num(timestamps)

    # Prevents errors when running on server
    matplotlib.pyplot.switch_backend('Agg') 
    # Plotting
    fig, ax = plt.subplots()
    ax.plot_date(timestamps_numeric, values, '-')

    # Formatting x-axis as datetime
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

    # Rotating x-axis labels for better readability (optional)
    plt.xticks(rotation=45)

    # Adding labels and title
    plt.xlabel('Date')
    plt.ylabel('Moisture %')
    plt.title('Moisture over time')

    # Show the plot
    # plt.show()

    # Save the plot to a PNG in memory
    #plt.savefig('static/img/plot.png', format='png', bbox_inches='tight')

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

def __load_env_file(env_file_path=".env"):
    try:
        with open(env_file_path, "r") as file:
            for line in file:
                # Ignore lines that are empty or start with '#'
                if not line.strip() or line.startswith("#"):
                    continue

                # Split the line at the first '=' character
                key, value = line.strip().split("=", 1)

                # Set the environment variable
                os.environ[key] = value

    except FileNotFoundError:
        print(f"{env_file_path} not found. Make sure to create a .env file with your environment variables.")

def __send_message():
    __load_env_file()
    url = os.getenv("URL")
    username = os.getenv("USER")
    password = os.getenv("PASS")

    # Replace these with your server's hostname and port
    active_mq_host = url
    active_mq_port = 61613

    # The ActiveMQ queue name
    destination_queue = 'controller.1.asset.model'
    # Your message
    message_to_send = '[MSG]Update the asset model'

    # Establish the STOMP connection
    conn = stomp.Connection([(active_mq_host, active_mq_port)])
    # Set the connection listener
    conn.set_listener('', StompConnectionListener())
    # Start the STOMP connection
    conn.connect(username, password, wait=True)

    # Send a message to the ActiveMQ queue
    conn.send(body=message_to_send, destination=destination_queue)

    # Sleep to allow for the message to be sent and received in the queue
    time.sleep(2)

    # Disconnect from the ActiveMQ server
    conn.disconnect()

@app.route('/submit', methods=['POST'])
def submit():
    # Get data from the form
    query = "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
            PREFIX ast: <http://www.smolang.org/greenhouseDT#> \
            PREFIX owl: <http://www.w3.org/2002/07/owl#> \
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> \
            INSERT { \
            ast:basilicum5 rdf:type owl:NamedIndividual , \
                                    ast:Basilicum ; \
                        ast:idealMoisture \"60.0\"^^xsd:double ; \
                        ast:plantId \"5\"^^xsd:string ; \
                        ast:plantType \"Basilicum\"^^xsd:string . \
            } \
            WHERE { \
            FILTER NOT EXISTS { ast:basilicum5 rdf:type ast:Basilicum . \
            } \
            } "
    
    data = {'update': query}
    # make a post request to http://localhost:3030/GreenHouse/update
    r = requests.post('http://localhost:3030/GreenHouse/update', data=data)

    # Process the data if needed
    result = f"Query submitted: {query}"

    # Return a JSON response
    return jsonify(result)

@app.route('/update_query', methods=['POST'])
def update_query():
    # Get data from the form
    query = request.form['query']

    data = {'update': query}
    # make a post request to http://localhost:3030/GreenHouse/update
    r = requests.post('http://localhost:3030/GreenHouse/update', data=data)

    # Process the data if needed
    status_code = r.status_code
    
    if status_code == 200:
        result = {'status': status_code, 'message': "Query submitted successfully"}
    elif status_code == 400:
        result = {'status': status_code, 'message': "Query failed: bad request"}
    elif status_code == 500:
        result = {'status': status_code, 'message': "Query failed: internal server error"}

    # Return a JSON response
    return json.dumps(result)

@app.route('/update_asset_model', methods=['POST'])
def update_asset_model():
    __send_message()
    result = {'status': 200, 'message': "Asset model updated successfully"}
    return json.dumps(result)

if __name__ == '__main__':
    app.run(debug=True)
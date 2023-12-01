function submitForm() {
  // Perform the POST request
  fetch('/submit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    }
  })
  .then(response => response.text())
  .then(result => {
    // Update the result container with the response
    document.getElementById('resultContainer').innerHTML = 'Result: ' + result.toString().replaceAll("<", "&lt;").replaceAll(">", "&gt;");
  });
}

function updateQuery() {
  // Get the query from the input field
  var query = document.getElementById('query').value;

  // Perform the POST request
  fetch('/update_query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'query=' + query
  })
  .then(response => response.json())
  .then(result => {
    console.log(typeof result); // log the type of result
    console.log(result);
    if (result.status == 200) {
      alert("Query executed successfully!");
    } else if (result.status == 500) {
      alert("Query execution failed: server error!");
    } else if (result.status == 400) {
      alert("Query execution failed: bad request!");
    }
  });
}

function getModel() {
  // Perform the POST request
  fetch('/get_model')
  .then(response => response.json())
  .then(result => {
    console.log(result);

    document.getElementById('plants').innerHTML = result.Plant.replace(/\n/g, "<br>");
    document.getElementById('pots').innerHTML = result.Pot.replace(/\n/g, "<br>");
    document.getElementById('pumps').innerHTML = result.Pump.replace(/\n/g, "<br>");
  });
}

function updateGraph() {
  // Fetch the new graph data from the server
  fetch('/get_graph')
    .then(response => response.json())
    .then(data => {
      console.log(data);
      // Update the src attribute with the new graph data
      document.getElementById('graphImage').src = 'data:image/png;base64,' + data.graph_data;
    });
}
function submitForm() {
  // Perform the POST request
  let button = document.getElementById("update-demo");
  button.disabled = true;

  fetch('/submit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    }
  })
  .then(response => response.text())
  .then(result => {
    button.disabled = false;
    // Update the result container with the response
    document.getElementById('resultContainer').innerHTML = 'Result: ' + result.toString().replaceAll("<", "&lt;").replaceAll(">", "&gt;");
  });
}

function updateQuery() {
  let button = document.getElementById("update-greenhouse");
  button.disabled = true;
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
      
      button.disabled = false;
      alert("Query executed successfully!");
    } else if (result.status == 500) {
      alert("Query execution failed: server error!");
    } else if (result.status == 400) {
      alert("Query execution failed: bad request!");
    }
  });
}

function updateAssetModel() {
  fetch('/update_asset_model', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    }
  })
  .then(response => response.json())
  .then(result => {
    console.log(result);
    if (result.status == 200) {
      alert("Asset model updated successfully!");
    } else if (result.status == 500) {
      alert("Asset model update failed: server error!");
    } else if (result.status == 400) {
      alert("Asset model update failed: bad request!");
    }
  });
}

function getModel() {
  // Perform the POST request
  fetch('/get_model')
  .then(response => response.json())
  .then(result => {
    console.log(result);

    document.getElementById('newPlant').innerHTML = result.Plant.added.replace(/\n/g, "<br>");
    document.getElementById('changedPlant').innerHTML = result.Plant.changed.replace(/\n/g, "<br>");
    document.getElementById('removedPlant').innerHTML = result.Plant.removed.replace(/\n/g, "<br>");

    document.getElementById('newPot').innerHTML = result.Pot.added.replace(/\n/g, "<br>");
    document.getElementById('changedPot').innerHTML = result.Pot.changed.replace(/\n/g, "<br>");
    document.getElementById('removedPot').innerHTML = result.Pot.removed.replace(/\n/g, "<br>");

    document.getElementById('newPump').innerHTML = result.Pump.added.replace(/\n/g, "<br>");
    document.getElementById('changedPump').innerHTML = result.Pump.changed.replace(/\n/g, "<br>");
    document.getElementById('removedPump').innerHTML = result.Pump.removed.replace(/\n/g, "<br>");

    // document.getElementById('plants').innerHTML = result.Plant.replace(/\n/g, "<br>");
    // document.getElementById('pots').innerHTML = result.Pot.replace(/\n/g, "<br>");
    // document.getElementById('pumps').innerHTML = result.Pump.replace(/\n/g, "<br>");
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
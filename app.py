from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # Pass data to the template
    text_content = "This is some text content."
    # You can add data for the matplotlib graph as needed

    return render_template('index.html', text_content=text_content)

if __name__ == '__main__':
    app.run(debug=True)
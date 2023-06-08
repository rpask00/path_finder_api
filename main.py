# Hello world in flask


from flask import Flask

# run on port 4700
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'

from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', project="AskOmics")

@app.route('/api/hello', methods=['GET', 'POST'])
def hello():

    if request.method == 'POST':
        json = request.get_json()
        data = {'message': 'Hello {}!'.format(json['name'])}
    else:
        data = {'message': 'hello!'}

    return jsonify(data)

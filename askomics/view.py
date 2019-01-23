from flask import render_template
from askomics import app

@app.route('/')
def home():
    return render_template('index.html', project="AskOmics")


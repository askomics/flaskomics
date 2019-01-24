"""Render route
"""
from flask import render_template
from askomics import app

@app.route('/')
def home():
    """Render the html of AskOmics

    Returns
    -------
    html
        Html code of AskOmics
    """
    return render_template('index.html', project="AskOmics")


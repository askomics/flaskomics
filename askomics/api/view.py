"""Render route
"""
from flask import (Blueprint, render_template)


view_bp = Blueprint('view', __name__, url_prefix='/')

@view_bp.route('/')
def home():
    """Render the html of AskOmics

    Returns
    -------
    html
        Html code of AskOmics
    """
    return render_template('index.html', project="AskOmics")

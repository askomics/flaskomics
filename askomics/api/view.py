"""Render route"""
from flask import (Blueprint, render_template, current_app)


view_bp = Blueprint('view', __name__, url_prefix='/')


@view_bp.route('/', defaults={'path': ''})
@view_bp.route('/<path:path>')
def home(path):
    """Render the html of AskOmics

    Returns
    -------
    html
        Html code of AskOmics
    """
    proxy_path = "/"
    try:
        proxy_path = current_app.iniconfig.get('askomics', 'reverse_proxy_path')
    except Exception:
        pass

    return render_template('index.html', project="AskOmics", proxy_path=proxy_path)

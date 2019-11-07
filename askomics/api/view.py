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

    # get sentry frontend dsn
    sentry_dsn = ""
    try:
        sentry_dsn = current_app.iniconfig.get("sentry", "frontend_dsn")
    except Exception:
        pass

    title = "AskOmics"
    try:
        subtitle = current_app.iniconfig.get('askomics', 'subtitle')
        title = "AskOmics | {}".format(subtitle)
    except Exception:
        pass

    return render_template('index.html', title=title, proxy_path=proxy_path, sentry=sentry_dsn)

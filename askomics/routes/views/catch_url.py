"""Catch_all route
"""
from flask import redirect, url_for
from askomics import app

@app.route('/<path:path>')
def catch_all(path):
    """Return all routes to home

    Parameters
    ----------
    path : str
        Original path

    Returns
    -------
    redirect
        Redirect to route /
    """


    return redirect(url_for('home'))
"""Catch_all route
"""
from flask import Blueprint, redirect

catch_url_bp = Blueprint('catch_url', __name__, url_prefix='/')


@catch_url_bp.route('/<path:path>')
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

    return redirect('/?path={}'.format(path))

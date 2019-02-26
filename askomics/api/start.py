from flask import (Blueprint, current_app, jsonify, request, session)
from pkg_resources import get_distribution

from askomics.libaskomics.Start import Start
from askomics.libaskomics.LocalAuth import LocalAuth


start_bp = Blueprint('start', __name__, url_prefix='/')

@start_bp.route('/api/hello', methods=['GET'])
def hello():
    """Dummy routes

    Returns
    -------
    json
        A welcome message
    """
    if 'user' in session:
        data = {
            'message':
            'Hello {} {}, welcome to AskOmics!'.format(session['user']['fname'],
                                                         session['user']['lname'])
        }
    else:
        data = {'message': 'Welcome to AskOmics!'}

    return jsonify(data)

@start_bp.route('/api/start', methods=['GET'])
def start():
    """Starting route

    Returns
    -------
    json
        Information about a eventualy logged user, and the AskOmics version
        and a footer message
    """
    starter = Start(current_app, session)
    starter.start()

    json = {
        "user": None,
        "logged": False,
        "version": get_distribution('askomics').version,
        "footer_message": current_app.iniconfig.get('askomics', 'footer_message')
    }

    if 'user' in session:
        local_auth = LocalAuth(current_app, session)
        user = local_auth.get_user(session['user']['username'])
        session['user'] = user
        json['user'] = user
        json['logged'] = True

    return jsonify(json)

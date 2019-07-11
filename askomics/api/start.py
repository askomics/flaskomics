import sys
import traceback

from askomics.libaskomics.LocalAuth import LocalAuth
from askomics.libaskomics.Start import Start

from flask import (Blueprint, current_app, jsonify, session)

from pkg_resources import get_distribution


start_bp = Blueprint('start', __name__, url_prefix='/')


@start_bp.route('/api/hello', methods=['GET'])
def hello():
    """Dummy routes

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
        message: a welcome message
    """
    try:
        message = "Welcome to AskOmics" if 'user' not in session else "Hello {} {}, Welcome to AskOmics!".format(
            session["user"]["fname"], session["user"]["lname"])

    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({
            'error': True,
            'errorMessage': '',
            'message': ''
        }), 500

    return jsonify({
        'error': False,
        'errorMessage': '',
        'message': message
    })


@start_bp.route('/api/start', methods=['GET'])
def start():
    """Starting route

    Returns
    -------
    json
        Information about a eventualy logged user, and the AskOmics version
        and a footer message
    """
    try:
        starter = Start(current_app, session)
        starter.start()

        config = {
            "footerMessage": current_app.iniconfig.get('askomics', 'footer_message'),
            "version": get_distribution('askomics').version,
            "disableIntegration": current_app.iniconfig.getboolean('askomics', 'disable_integration'),
            "prefix": current_app.iniconfig.get('triplestore', 'prefix'),
            "namespace": current_app.iniconfig.get('triplestore', 'namespace')
        }

        json = {
            "error": False,
            "errorMessage": '',
            "user": None,
            "logged": False,
            "config": config
        }

        if 'user' in session:
            local_auth = LocalAuth(current_app, session)
            user = local_auth.get_user(session['user']['username'])
            session['user'] = user
            json['user'] = user
            json['logged'] = True

        return jsonify(json)

    except Exception as e:
        current_app.logger.error(str(e))
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            "error": True,
            "errorMessage": str(e),
            "user": None,
            "logged": False,
            "config": {}
        }), 500

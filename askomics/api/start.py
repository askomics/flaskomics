import git
import sys
import traceback

from askomics.api.auth import api_auth
from askomics.libaskomics.LocalAuth import LocalAuth
from askomics.libaskomics.Start import Start
from askomics.libaskomics.OntologyManager import OntologyManager

from flask import (Blueprint, current_app, jsonify, session)

from pkg_resources import get_distribution


start_bp = Blueprint('start', __name__, url_prefix='/')


@start_bp.route('/api/start', methods=['GET'])
@api_auth
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

        # Get commmit hash
        sha = None
        if current_app.iniconfig.getboolean('askomics', 'display_commit_hash'):
            try:
                repo = git.Repo(search_parent_directories=True)
                sha = repo.head.object.hexsha[:10]
            except Exception:
                pass

        front_message = None
        try:
            front_message = current_app.iniconfig.get('askomics', 'front_message')
        except Exception:
            pass

        contact_message = None
        try:
            contact_message = current_app.iniconfig.get('askomics', 'contact_message')
        except Exception:
            pass

        # get proxy path
        proxy_path = "/"
        try:
            proxy_path = current_app.iniconfig.get("askomics", "reverse_proxy_path")
        except Exception:
            pass

        # Get ldap password reset link if set
        password_reset_link = None
        try:
            password_reset_link = current_app.iniconfig.get("askomics", "ldap_password_reset_link")
        except Exception:
            pass
        # Get ldap password reset link if set
        account_link = None
        try:
            account_link = current_app.iniconfig.get("askomics", "ldap_account_link")
        except Exception:
            pass

        ontologies_manager = OntologyManager(current_app, session)
        ontologies = ontologies_manager.list_ontologies()

        config = {
            "footerMessage": current_app.iniconfig.get('askomics', 'footer_message'),
            "frontMessage": front_message,
            "contactMessage": contact_message,
            "version": get_distribution('askomics').version,
            "commit": sha,
            "gitUrl": current_app.iniconfig.get('askomics', 'github'),
            "disableAccountCreation": current_app.iniconfig.getboolean("askomics", "disable_account_creation"),
            "disableIntegration": current_app.iniconfig.getboolean('askomics', 'disable_integration'),
            "protectPublic": current_app.iniconfig.getboolean('askomics', 'protect_public'),
            "passwordResetLink": password_reset_link,
            "accountLink": account_link,
            "namespaceData": current_app.iniconfig.get('triplestore', 'namespace_data'),
            "namespaceInternal": current_app.iniconfig.get('triplestore', 'namespace_internal'),
            "proxyPath": proxy_path,
            "user": {},
            "logged": False,
            "ontologies": ontologies,
            "singleTenant": current_app.iniconfig.getboolean('askomics', 'single_tenant', fallback=False),
            "autocompleteMaxResults": current_app.iniconfig.getint("askomics", "autocomplete_max_results", fallback=10),
            "anonymousQuery": current_app.iniconfig.get('askomics', 'anonymous_query', fallback=False)
        }

        json = {
            "error": False,
            "errorMessage": '',
            "config": config
        }

        if 'user' in session:
            local_auth = LocalAuth(current_app, session)
            user = local_auth.get_user(session['user']['username'])
            local_auth.update_last_action(session["user"]["username"])
            session['user'] = user
            json['config']['user'] = user
            json['config']['logged'] = True

        return jsonify(json)

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            "error": True,
            "errorMessage": str(e),
            "config": {}
        }), 500

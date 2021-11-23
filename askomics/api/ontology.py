import traceback
import sys
from askomics.api.auth import api_auth, login_required
from askomics.libaskomics.OntologyManager import OntologyManager

from flask import (Blueprint, current_app, jsonify, request, session)

onto_bp = Blueprint('ontology', __name__, url_prefix='/')


@onto_bp.route("/api/ontology/<short_ontology>/autocomplete", methods=["GET"])
@api_auth
@login_required
def autocomplete(short_ontology):
    """Get the default sparql query

    Returns
    -------
    json
    """

    if not request.args.get("q"):
        return jsonify({
            "error": True,
            "errorMessage": "Missing q parameter",
            "results": []
        }), 400

    try:
        # Disk space
        om = OntologyManager(current_app, session)
        ontology = om.get_ontology(short_ontology)
        if not ontology:
            return jsonify({
                "error": True,
                "errorMessage": "Ontology {} not found".format(short_ontology),
                "results": []
            }), 404

        results = om.autocomplete(ontology["uri"], ontology["type"], request.args.get("q"))

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            "error": True,
            "errorMessage": str(e),
            "results": []
        }), 404

    return jsonify({
        "error": True,
        "errorMessage": "",
        "results": results
    }), 200

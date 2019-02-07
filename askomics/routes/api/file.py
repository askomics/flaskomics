"""Api routes
"""
from flask import jsonify, session, request
from askomics import app, login_required
from askomics.libaskomics.Files import Files

@app.route('/api/files', methods=['GET'])
@login_required
def get_files():

    files_handler = Files(app, session)
    files = files_handler.get_files()

    return jsonify({'files': files})

@app.route('/api/file/upload', methods=['POST'])
@login_required
def upload():


    inputs = request.files

    files = Files(app, session, new_files=inputs)
    uploaded_files = files.persist_files()

    return jsonify({'uploadedFiles': uploaded_files})

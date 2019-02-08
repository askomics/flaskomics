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

@app.route('/api/files/upload', methods=['POST'])
@login_required
def upload():


    inputs = request.files

    files = Files(app, session, new_files=inputs)
    uploaded_files = files.persist_files()

    return jsonify({'uploadedFiles': uploaded_files})

@app.route('/api/files/delete', methods=['POST'])
@login_required
def delete_files():

    data = request.get_json()

    files = Files(app, session)
    remaining_files = files.delete_files(data['filesIdToDelete'])

    return jsonify({
        'files': remaining_files
    })

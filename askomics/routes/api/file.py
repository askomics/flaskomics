"""Api routes
"""
from flask import jsonify, session, request
from askomics import app, login_required
from askomics.libaskomics.Files import Files
from askomics.libaskomics.FilesHandler import FilesHandler

@app.route('/api/files', methods=['GET', 'POST'])
@login_required
def get_files():

    files_id = None
    if request.method == 'POST':
        data = request.get_json()
        app.logger.debug(data)
        files_id = data['filesId']

    files_handler = Files(app, session)
    files = files_handler.get_files(files_id=files_id)

    return jsonify({'files': files})

@app.route('/api/files/upload', methods=['POST'])
@login_required
def upload():


    inputs = request.files

    files = Files(app, session, new_files=inputs)
    uploaded_files = files.persist_files()

    return jsonify({'uploadedFiles': uploaded_files})

@app.route('/api/files/preview', methods=['POST'])
@login_required
def get_preview():

    data = request.get_json()

    database_files = Files(app, session)
    files_infos = database_files.get_files_with_path(data['filesId'])

    files_handler = FilesHandler(app, session, files_infos)

    for file in files_handler.files:
        file.set_preview_and_header()
        file.set_columns_type()
        app.logger.debug(file.header)
        app.logger.debug(file.preview)
        app.logger.debug(file.columns_type)






    return jsonify({})

@app.route('/api/files/delete', methods=['POST'])
@login_required
def delete_files():

    data = request.get_json()

    files = Files(app, session)
    remaining_files = files.delete_files(data['filesIdToDelete'])

    return jsonify({
        'files': remaining_files
    })

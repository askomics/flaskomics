"""Api routes
"""
from flask import (Blueprint, current_app, jsonify, session, request, send_from_directory)
from askomics.api.auth import login_required
from askomics.libaskomics.FilesHandler import FilesHandler
from askomics.libaskomics.File import File

file_bp = Blueprint('file', __name__, url_prefix='/')

@file_bp.route('/api/files', methods=['GET', 'POST'])
@login_required
def get_files():

    files_id = None
    if request.method == 'POST':
        data = request.get_json()
        files_id = data['filesId']

    try:
        files_handler = FilesHandler(current_app, session)
        files = files_handler.get_files_infos(files_id=files_id)
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({
            'files': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'files': files,
        'error': False,
        'errorMessage': ''
    })

@file_bp.route('/api/files/upload', methods=['POST'])
@login_required
def upload():

    inputs = request.files

    try:
        files = FilesHandler(current_app, session)
        uploaded_files = files.persist_files(inputs)
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({
            'uploadedFiles': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'uploadedFiles': uploaded_files,
        'error': False,
        'errorMessage': ''
    })

@file_bp.route('/api/files/preview', methods=['POST'])
@login_required
def get_preview():

    data = request.get_json()

    try:
        files_handler = FilesHandler(current_app, session)
        files_handler.handle_files(data['filesId'])

        results = []
        for file in files_handler.files:
            file.set_preview()
            res = file.get_preview()
            results.append(res)
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({
            'previewFiles': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'previewFiles': results,
        'error': False,
        'errorMessage': ''
    })

@file_bp.route('/api/files/delete', methods=['POST'])
@login_required
def delete_files():

    data = request.get_json()

    try:
        files = FilesHandler(current_app, session)
        remaining_files = files.delete_files(data['filesIdToDelete'])
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({
            'files': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'files': remaining_files,
        'error': False,
        'errorMessage': ''
    })

@file_bp.route('/api/files/integrate', methods=['POST'])
@login_required
def integrate():

    data = request.get_json()

    session_dict = {'user': session['user']}

    try:
        task = current_app.celery.send_task('integrate', (session_dict, data, request.host_url))
        # task = async_integrate.delay(data, request.host_url)
        current_app.logger.debug(task)
    except Exception as e:
            return jsonify({
                'error': True,
                'errorMessage': str(e),
                'task_id': None
            }), 500

    return jsonify({
        'error': False,
        'errorMessage': '',
        'task_id': task.id
    })


@file_bp.route('/files/ttl/<path:user_id>/<path:username>/<path:path>')
def serve_file(path, user_id, username):

    dir_path = "{}/{}_{}/ttl".format(
        current_app.iniconfig.get('askomics', 'data_directory'),
        user_id,
        username
    )

    return(send_from_directory(dir_path, path))

# @celery.task()
# def async_integrate(data, host_url):

#     # import time
#     # with open('/home/xgarnier/Desktop/coucou.txt', 'w') as file:
#     #     file.write(str(time.time()))


#     files_handler = FilesHandler(app, session, host_url=host_url)
#     files_handler.handle_files([data["fileId"], ])

#     for file in files_handler.files:

#         try:
#             file.integrate(data['columns_type'])
#         except Exception as e:
#             app.logger.error(str(e))
#             # Rollback
#             file.rollback()
#             return 'error'
#             # return jsonify({
#             #     'error': True,
#             #     'errorMessage': str(e)
#             # }), 500

#     app.logger.debug('DONE')
#     return 'DONE'

#     # return jsonify({
#     #     'error': False,
#     #     'errorMessage': ''
#     # })

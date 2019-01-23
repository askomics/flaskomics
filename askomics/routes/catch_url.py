from flask import redirect, url_for
from askomics import app

@app.route('/<path:path>')
def catch_all(path):
    return redirect(url_for('home'))
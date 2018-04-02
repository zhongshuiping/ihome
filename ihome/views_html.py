from flask import Blueprint,make_response
from flask_wtf import csrf

static_html = Blueprint('static_html',__name__,static_folder='static/html')


@static_html.route('/<re(".*"):filename>')
def show_html(filename):

    if not filename:
        filename = 'index.html'
    response = make_response(static_html.send_static_file(filename))
    csrf_token = csrf.generate_csrf()
    response.set_cookie('csrf_token',csrf_token)
    return response
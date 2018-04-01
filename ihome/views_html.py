from flask import Blueprint


static_html = Blueprint('static_html',__name__,static_folder='static/html')


@static_html.route('/<re(".*"):filename>')
def show_html(filename):

    if not filename:
        filename = 'index.html'

    return static_html.send_static_file(filename)
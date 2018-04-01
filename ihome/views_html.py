from flask import Blueprint

static_html = Blueprint('static_html',__name__)


@static_html.route('/<filename>')
def show_html(filename):
    return filename
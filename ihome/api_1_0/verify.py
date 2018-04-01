from . import api
from ihome.utils.captcha.captcha import captcha
from flask import make_response


@api.route('/verify')
def verify():

    name, text, image = captcha.generate_captcha()
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'
    return response
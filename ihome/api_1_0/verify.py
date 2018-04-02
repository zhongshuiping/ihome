from . import api
from ihome.utils.captcha.captcha import captcha
from flask import make_response, request, current_app
from config import Config

redis = Config.get_redis_connect()


@api.route('/verify_code')
def verify():
    name, text, image = captcha.generate_captcha()
    uuid = request.args.get('uuid')
    last_uuid = request.args.get('last_uuid')
    try:
        if last_uuid:
            redis.delete(last_uuid)
        redis.set(uuid, text, ex=60 * 5)
    except Exception as e:
        current_app.logger.error(e)

    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'
    return response

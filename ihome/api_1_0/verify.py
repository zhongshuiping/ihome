from . import api
from ihome.utils.captcha.captcha import captcha
from flask import make_response, request, current_app
from config import Config
from ihome import constants
# 获取redis数据库的链接
redis = Config.get_redis_connect()


@api.route('/verify_code')
def verify():
    name, text, image = captcha.generate_captcha()
    uuid = request.args.get('uuid')
    last_uuid = request.args.get('last_uuid')
    current_app.logger.debug(text)

    try:
        if last_uuid:
            redis.delete('image_code:'+last_uuid)
        redis.set('image_code:'+uuid, text, ex=constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)

    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'
    return response

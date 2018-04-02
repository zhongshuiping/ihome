from . import api
from ihome.utils.captcha.captcha import captcha
from flask import make_response, request, current_app,jsonify
from config import Config
from ihome import constants
from ihome.utils.response_code import RET
import re
import random
from ihome.libs.yuntongxun.sms import CCP


# 获取redis数据库的链接
redis = Config.get_redis_connect()

@api.route('/sms_code',methods=['POST'])  #发送短信验证码
def sms():
    #首先要接收数据,对数据进行验证,只有验证通过才能发送短信,需要接收三个数据,手机号码 验证码 uuid
    data = request.get_json()
    mobile_client = data.get('mobile')
    image_code = data.get('image_code')

    uuid = data.get('uuid')

    if not all([mobile_client,image_code,uuid]):
        return jsonify({'errno':RET.PARAMERR,'errmsg':'参数不全'})

    if not re.match('^1[358]\d{9}$|^147\d{8}$|^176\d{8}$',mobile_client):
        return jsonify({'errno':RET.PARAMERR,'errmsg':'手机号码错误'})
    image_code_server = redis.get('image_code:'+uuid)

    if not image_code_server:
        return jsonify({'errno':RET.NODATA,'errmsg':'验证码过期'})

    if image_code_server.decode('utf-8').lower() != image_code.lower():
        return jsonify({'errno': RET.PARAMERR, 'errmsg': '验证码错误'})
    try:
        sms_code = '%04d' % random.randint(0,9999)
        current_app.logger.debug('短信验证码'+sms_code)
        # 设置短信验证码到数据库
        redis.set('sms_code:'+mobile_client+uuid,sms_code,ex=constants.SMS_CODE_REDIS_EXPIRES)
        ret = CCP().send_template_sms(mobile_client, ["1234", "5"], 1)
        if ret == 0:
            return jsonify({'errno':RET.OK,'errmsg':'发送短信成功'})
        else:
            return jsonify({'errno':RET.SERVERERR,'errmsg':'发送短信失败,请明天再试'})
    except Exception as e:
        return jsonify({'errno':RET.DATAERR,'errmsg':'保存短信验证码失败'})


@api.route('/verify_code')
def verify():
    name, text, image = captcha.generate_captcha()
    uuid = request.args.get('uuid')
    last_uuid = request.args.get('last_uuid')
    current_app.logger.debug('验证码:'+text)

    try:
        if last_uuid:
            redis.delete('image_code:'+last_uuid)
        redis.set('image_code:'+uuid, text, ex=constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)

    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'
    return response

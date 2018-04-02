from flask import request,jsonify,current_app
from . import api
from ihome.utils.response_code import RET
import re
from config import Config

from ihome.models import User

redis = Config.get_redis_connect()

@api.route('/users',methods=['POST'])
def register():
    '''对用户的注册的认证'''
    # 需要接收三个参数 第一个是手机号码 短信验证码 密码,uuid
    data = request.get_json()
    mobile_client = data.get('mobile')
    sms_code = data.get('sms_code')
    uuid = data.get('uuid')
    password = data.get('password')

    if not all([mobile_client,sms_code,uuid]):
        return jsonify({'errno':RET.PARAMERR,'errmsg':'参数不全'})

    if not re.match('^1[358]\d{9}$|^147\d{8}$|^176\d{8}$',mobile_client):
        return jsonify({'errno':RET.PARAMERR,'errmsg':'手机号码错误'})

    sms_code_server = redis.get('sms_code:'+mobile_client+uuid)
    if not sms_code_server:
        return jsonify({'errno':RET.NODATA,'errmsg':'手机号码或者验证码错误'})

    if sms_code_server.decode('utf-8') != sms_code:
        return jsonify({'errno':RET.DATAERR,'errmsg':'验证码错误'})
    try:
        from ihome import db
        user = User(name=mobile_client,mobile=mobile_client)
        user.password = password
        db.session.add(user)
        db.session.commit()
        return jsonify({'errno':RET.OK,'errmsg':'注册成功'})
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify({'errno':RET.SERVERERR,'errmsg':'插入user到数据库失败'})
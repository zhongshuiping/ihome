from flask import request,jsonify,current_app,session,g
from . import api
from ihome.utils.response_code import RET
import re
from config import Config
from ihome.models import User

redis = Config.get_redis_connect()

'''
退出登陆
'''
@api.route('/sessions',methods=['DELETE'])
def logout():
    session.pop('user_id')
    session.pop('username')
    return jsonify({'errno':RET.OK,'errmsg':'退出成功'})

'''
用户注册的逻辑
'''
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

'''
用户登陆的接口
'''
@api.route('/sessions',methods=['POST'])
def login():
    data = request.get_json()
    mobile = data.get('mobile')
    password = data.get('password')

    if not all([mobile,password]):
        return jsonify({'errno':RET.PARAMERR,'errmsg':'参数不完整'})

    if not re.match('^1[358]\d{9}$|^147\d{8}$|^176\d{8}$',mobile):
        return jsonify({'errno':RET.PARAMERR,'errmsg':'手机号码错误'})
    try:
        user = User.query.filter_by(mobile=mobile).first()
        if not user:
            return jsonify({'errno':RET.NODATA,'errmsg':'用户名或者密码错误'})
    except Exception as e:
        return jsonify({'errno':RET.DBERR,'errmsg':'数据库查询失败'})

    if not user.check_password(password):
        return jsonify({'errno':RET.NODATA,'errmsg':'用户名或者密码错误'})

    session['user_id'] = user.id
    session['username'] = user.name

    return jsonify({'errno':RET.OK,'errmsg':'登陆成功'})

'''
判断用户是否登陆
'''
@api.route('/sessions')
def check_login():

    user_id = session.get('user_id')
    username = session.get('username')
    if not user_id:
        return jsonify({'errno':RET.SESSIONERR,'errmsg':'没有登陆'})
    try:
        user = User.query.get(user_id)
    except Exception as e:
        return jsonify({'errno':RET.DBERR,'errmsg':'查询用户失败'})
    flag = 0   #是否实名认证,1代码有实名认证 0 表示没有
    if user.real_name and user.id_card:
        flag = 1

    to_dict = {
        'username':username,
        'flag':flag
    }
    return jsonify({'errno':RET.OK,'errmsg':'已经登陆','data':to_dict})
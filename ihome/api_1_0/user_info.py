from flask import session,jsonify,request,current_app,g
from . import api
from ihome.utils.response_code import RET
from ihome.models import User
from ihome.utils.qiniu_image import upload_image
from ihome.constants import QINIU_URL_DOMAIN
from ihome import db
from ihome.utils.common import login_required
import re
'''
查询用户的信息
'''
@api.route('/users')
@login_required
def users():
    try:
        user_id = g.user_id
        user = User.query.filter(User.id == user_id).first()
    except Exception as e:
        return jsonify({'errno':RET.NODATA,'errmsg':'请登陆'})
        current_app.logger.error(e)

    if not user:
        return jsonify({'errno':RET.NODATA,'errmsg':'查询用户失败'})

    return jsonify({'errno':RET.OK,'errmsg':'ok','data':user.to_dict()})

'''
上传图片到七牛文件服务器
'''
@api.route('/avatar',methods=['POST','GET'])
@login_required
def avatar():
    user_id = g.user_id
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return jsonify({'errno': RET.SESSIONERR, 'errmsg': '查询不到这个用户'})

    if request.method == 'POST':
        avatar = request.files.get('avatar')
        if not avatar:
            return jsonify({'errno':RET.DATAERR,'errmsg':'没有上传图片'})
        try:

            key = upload_image(avatar.stream.read())

        except Exception as e:
            current_app.logger.error(e)
            return jsonify({'errno':RET.IOERR,'errmsg':'服务器错误,请稍后再试'})
        try:

            user.avatar_url = QINIU_URL_DOMAIN + key
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify({'errno':RET.NODATA,'errmsg':'查询或者插入数据错误'})

        data = {
            'avatar_url':user.avatar_url
        }
        return jsonify({'errno':RET.OK,'errmsg':'上传文件成功','data':data})
    else:
        data = {
            'avatar_url': user.avatar_url
        }
        return jsonify({'errno':RET.OK,'errmsg':'查询图片','data':data})

'''
用户名修改
'''
@api.route('/name',methods=['PUT'])
@login_required
def update_name():

    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'errno':RET.NODATA,'errmsg':'修改的用户名不能为空'})
    try:
        user_id = g.user_id
        user = User.query.get(user_id)
        user.name = name
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'errno':RET.DATAERR,'errmsg':'查询数据库失败'})
    return jsonify({'errno':RET.OK,'errmsg':'修改成功'})

'''
用户实名认证
'''
@api.route('/user/auth',methods=['POST','GET'])
@login_required
def auth():
    user_id = g.user_id
    user = User.query.filter(User.id == user_id).first()
    if request.method == 'POST':
        data = request.get_json()
        real_name = data.get('real_name')
        id_card = data.get('id_card')

        if not all([real_name,id_card]):
            return jsonify({'errno':RET.PARAMERR,'errmsg':'参数不完整'})
        if not re.match(r'\d+',id_card):
            return jsonify({'errno':RET.DATAERR,'errmsg':'请填写正确的身份证号码'})

        user.id_card = id_card
        user.real_name = real_name
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify({'errno':RET.DATAERR,'errmsg':'添加信息失败'})

        return jsonify({'errno':RET.OK,'errmsg':'认证信息保存成功'})
    else:

        return jsonify({'errno':RET.OK,'errmsg':'查询成功','data':user.to_data()})
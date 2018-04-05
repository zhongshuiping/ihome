from flask import session,jsonify,request,current_app
from . import api
from ihome.utils.response_code import RET
from ihome.models import User
from ihome.utils.qiniu_image import upload_image
from ihome.constants import QINIU_URL_DOMAIN
from ihome import db

'''
查询用户的信息
'''
@api.route('/users')
def users():
    try:
        user_id = session.get('user_id')
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
def avatar():
    user_id = session.get('user_id')
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


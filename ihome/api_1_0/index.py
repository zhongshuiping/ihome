from . import api
from config import Config
from flask import request,jsonify


@api.route('/',methods=['POST'])
def index():

    data = request.get_json()
    try:
        mobile = data.get('mobile')
        password = data.get('password')
    except Exception as e:
        return jsonify(errno=0, errmeg='填写的参数有误')

    if not all([mobile,password]):
        return jsonify(errno=1,errmeg='参数不完整')
    return 'index'
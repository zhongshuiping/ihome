from werkzeug.routing import BaseConverter
from flask import session,jsonify,g
from ihome.utils.response_code import RET
from functools import wraps

class RegxConverter(BaseConverter):

    def __init__(self,map,*args):
        super(RegxConverter, self).__init__(map)
        self.regex = args[0]


def login_required(view_func):

    @wraps(view_func)
    def wrapper(*args,**kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'errno':RET.SESSIONERR,'errmsg':'请登陆'})
        g.user_id = user_id
        return view_func(*args,**kwargs)
    return wrapper
from flask import session
from . import api

@api.route('/users',methods=['GET'])
def users():
    pass
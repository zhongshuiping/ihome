from . import api
from config import Config

@api.route('/index')
def index():
    redis_store = Config.get_redis_connect()
    redis_store.set('name','zsp')
    return 'index'
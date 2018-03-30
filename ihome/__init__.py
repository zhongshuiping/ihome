from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import Config
from ihome.api_1_0 import api


"""工厂方法，根据外界传入的不同参数，实例化出不同场景下的app实例"""

app = Flask(__name__)

# 加载配置
app.config.from_object(Config)

# 创建连接到mysql实例

db = SQLAlchemy(app)



app.register_blueprint(api, url_prefix='/api/v1.0')

# 创建redis数据库实例
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 开启CSRF保护:制作校验. 没有设置csrf的cookie和表单的csrf_token
csrf = CSRFProtect(app)
# 指定session数据保存的位置
Session(app)



from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import map_config
from ihome.api_1_0 import api
from .views_html import static_html
from .utils.common import RegxConverter

db = SQLAlchemy()

"""工厂方法，根据外界传入的不同参数，实例化出不同场景下的app实例"""
def genarate(type):
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(map_config[type])

    # 创建连接到mysql实例

    db.init_app(app)
    #注册自定义的转换器
    app.url_map.converters['re'] = RegxConverter

    #注册api的路径
    app.register_blueprint(api, url_prefix='/api/v1_0')
    #注册查找静态页面的路由
    app.register_blueprint(static_html)

    # 开启CSRF保护:制作校验. 没有设置csrf的cookie和表单的csrf_token
    CSRFProtect(app)
    # 指定session数据保存的位置
    Session(app)
    return app



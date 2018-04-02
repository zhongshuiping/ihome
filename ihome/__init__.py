from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import map_config

from .views_html import static_html
from .utils.common import RegxConverter
import logging
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()

def config_logging(level):
    # 配置日志信息
    # 设置日志的记录等级
    logging.basicConfig(level=level)
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日记录器
    logging.getLogger().addHandler(file_log_handler)




"""工厂方法，根据外界传入的不同参数，实例化出不同场景下的app实例"""
def genarate(type):
    app = Flask(__name__)
    #配置日志级别,只要是生成环境和调试环境的logging不同
    config_logging(map_config[type].LEVEL)
    # 加载配置
    app.config.from_object(map_config[type])

    # 创建连接到mysql实例

    db.init_app(app)
    #注册自定义的转换器
    app.url_map.converters['re'] = RegxConverter

    #注册api的路径
    from ihome.api_1_0 import api
    app.register_blueprint(api, url_prefix='/api/v1_0')
    #注册查找静态页面的路由
    app.register_blueprint(static_html)

    # 开启CSRF保护:制作校验. 没有设置csrf的cookie和表单的csrf_token
    CSRFProtect(app)
    # 指定session数据保存的位置
    Session(app)
    return app



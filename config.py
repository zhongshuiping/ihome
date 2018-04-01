import redis
import uuid


class Config(object):

    SECRET_KEY = uuid.uuid4().hex

    DEBUG = True

    # 数据库的配置信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@192.168.182.138:3306/iHome"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # session 配置
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒

    @classmethod
    def get_redis_connect(cls):
        return redis.StrictRedis(host=cls.REDIS_HOST, port=cls.REDIS_PORT)

class DevConfig(Config):
    pass


class ProConfig(Config):
    DEBUG = False

    # 数据库的配置信息

class UtestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@192.168.182.137:3306/iHome_test"

map_config = {
    'default':Config,
    'dev':DevConfig,
    'pro':ProConfig,
    'test':UtestConfig
}

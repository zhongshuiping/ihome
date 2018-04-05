import qiniu
from flask import current_app

access_key = "yV4GmNBLOgQK-1Sn3o4jktGLFdFSrlywR2C-hvsW"
secret_key = "bixMURPL6tHjrb8QKVg2tm7n9k8C7vaOeQ4MEoeW"
bucket_name = 'ihome'


def upload_image(data):
    """
    上传图片到七牛云
    :param data: 要上传的文件数据
    :return:
    """

    q = qiniu.Auth(access_key, secret_key)
    token = q.upload_token(bucket_name)
    ret, info = qiniu.put_data(token, None, data)

    print (ret, info)
    # 判断是否上传成功
    if info.status_code == 200:
        # 如果上传成功就返回key
        return ret.get('key')
    else:
        raise Exception('上传失败')


# if __name__ == '__main__':
#     # 测试去上传一个本地文件
#
#     with open('mm02.jpg', 'rb') as file:
#         upload_image(file.read())
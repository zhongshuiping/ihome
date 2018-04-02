# coding=gbk

# coding=utf-8

# -*- coding: UTF-8 -*-

from ihome.libs.yuntongxun.CCPRestSDK import REST


# ���ʺ�
accountSid = '8a216da8627648690162809f02350160'

# ���ʺ�Token
accountToken = '6f9447658d834efcbb13a3dbdcd3741f'

# Ӧ��Id
appId = '8a216da8627648690162809f029a0167'

# �����ַ����ʽ���£�����Ҫдhttp://
serverIP = 'app.cloopen.com'

# ����˿�
serverPort = '8883'

# REST�汾��
softVersion = '2013-12-26'


# ����ģ�����
# @param to �ֻ�����
# @param datas �������� ��ʽΪ�б� ���磺['12','34']���粻���滻���� ''
# @param $tempId ģ��Id

class CCP(object):
    """�Լ���װ�ķ��Ͷ��ŵĸ�����"""
    # ������������������
    instance = None

    def __new__(cls):
        # �ж�CCP����û���Ѿ������õĶ������û�У�����һ�����󣬲��ұ���
        # ����У��򽫱���Ķ���ֱ�ӷ���
        if cls.instance is None:
            obj = super(CCP, cls).__new__(cls)

            # ��ʼ��REST SDK
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)

            cls.instance = obj

        return cls.instance

    def send_template_sms(self, to, datas, temp_id):
        """"""
        result = self.rest.sendTemplateSMS(to, datas, temp_id)

        status_code = result.get("statusCode")

        if status_code == "000000":
            # ��ʾ���Ͷ��ųɹ�
            return 0
        else:
            # ����ʧ��
            return -1


if __name__ == '__main__':
    ccp = CCP()
    ret = ccp.send_template_sms("13774672745", ["1234", "5"], 1)
    print(ret)

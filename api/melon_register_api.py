# melon 平台注册接口封装
import re
from http.client import responses

import requests


class MelonRegistrationSession:
    """
    Melon注册会话管理类，确保所有API调用在同一个会话中进行
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.server_token = None
        self.base_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        # 设置默认headers
        self.session.headers.update(self.base_headers)
    
    def get_server_token(self):
        """
        请求获取join页面，然后从join页面中获取解析到serverToken
        :return: 返回serverToken
        """
        url = 'https://gaccounts.melon.com/ticketGlobal/join?cpId=MP19&lang=EN&redirectUrl=https%3A%2F%2Ftkglobal.melon.com%2Fmain%2Findex.htm%3FlangCd%3DEN'
        response = self.session.get(url)
        print(f"[获取serverToken] 状态码: {response.status_code}")
        print(f"[获取serverToken] Cookies: {dict(response.cookies)}")
        
        pattern = r"joinForm\.append\(\$\('<input\/>'\, \{type: 'hidden', name: 'serverToken', value: \"([^\"]+)\" \}\)\);"
        match = re.search(pattern, response.text)
        if match:
            self.server_token = match.group(1)
            print("[获取serverToken]: ", self.server_token)
            return self.server_token
        return None


    def submit_auth_form(self, firstName: str, lastName: str, email: str, password: str, serverToken: str = None):
        """
        melon平台注册验证表单请求
        表单信息是通过密钥加密后的
        :param firstName: 姓
        :param lastName: 名
        :param email: 邮箱
        :param password: 密码
        :param serverToken: serverToken，如果为None则使用实例中的token
        :return:
        """
        if serverToken is None:
            serverToken = self.server_token
        
        url = 'https://gaccounts.melon.com/ticketGlobal/authForJoin'
        data = {
            'firstName': firstName,
            'lastName': lastName,
            'email': email,
            'password': password,
            'rePassword': password,
            'cpId': 'MP19',
            'lang': 'EN',
            'termsUserAgreement': 'Y',
            'termsPrivacyPolicy': 'Y',
            'termsOvsTransPInfo': 'Y',
            'redirectUrl': 'https://tkglobal.melon.com/main/index.htm?langCd=EN',
            'serverToken': serverToken
        }
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://gaccounts.melon.com',
            'Referer': 'https://gaccounts.melon.com/ticketGlobal/join?cpId=MP19&lang=EN&redirectUrl=https%3A%2F%2Ftkglobal.melon.com%2Fmain%2Findex.htm%3FlangCd%3DEN',
        }
        
        response = self.session.post(url, headers=headers, data=data, allow_redirects=False)
        print(f"[提交注册申请表] 状态码: {response.status_code}")
        print(f"[提交注册申请表] 响应头: {dict(response.headers)}")
        
        # 检查是否是重定向
        if response.status_code in [301, 302]:
            print(f"[提交注册申请表] 重定向到: {response.headers.get('Location')}")
            return f"重定向: {response.headers.get('Location')}"
        
        response_text = response.text
        print(f"[提交注册申请表] 响应长度: {len(response_text)}")
        
        # 检查响应内容
        if '<html>' in response_text.lower():
            print("[提交注册申请表] 警告: 返回了HTML页面")
            # 检查是否包含错误信息
            if 'error' in response_text.lower():
                print("[提交注册申请表] 发现错误信息")
            if 'valid' in response_text.lower():
                print("[提交注册申请表] 发现验证信息")
            if 'join' in response_text.lower():
                print("[提交注册申请表] 发现join相关信息")
        
        return response_text

    def send_email_for_join(self, email: str):
        """
        发送验证码邮件
        :param email: 邮箱地址
        :return:
        """
        url = 'https://gaccounts.melon.com/ticketGlobal/reSendEmailForJoin'
        data = {
            'email': email,
        }

        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Origin': 'https://gaccounts.melon.com',
            'Referer': 'https://gaccounts.melon.com/ticketGlobal/authForJoin',
            'X-Requested-With': 'XMLHttpRequest'
        }
        response = self.session.post(url, headers=headers, data=data)
        print("[发送邮件验证码]: ", response.status_code)
        print("[发送邮件验证码]: ", response.text)
        return response.text


    def is_already_exist_email(self, email: str):
        """
        检查邮箱是否已经存在
        :param email: 邮箱
        :return: 如果存在就返回true，否则就返回false
        """
        url = 'https://gaccounts.melon.com/ticketGlobal/isAlreadyExistEmail'
        data = {'email': email}
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://gaccounts.melon.com',
            'Referer': 'https://gaccounts.melon.com/ticketGlobal/authForJoin',
            'X-Requested-With': 'XMLHttpRequest',
        }
        response = self.session.post(url, headers=headers, data=data)
        print("[验证邮箱存在]", response.status_code)
        print("[验证邮箱存在]", response.text)
        res = response.json()
        if res is None:
            return False
        if res['isAlreadyExistEmail']:
            return True
        else:
            return False

    def valid_auth_key_for_join(self, email: str, code: str):
        """
        验证邮件验证码，获取serverToken
        :param email: 邮箱
        :param code: 验证码
        :return:
        """
        url = 'https://gaccounts.melon.com/ticketGlobal/validAuthKeyForJoin'
        data = {
            'email': email,
            'authKey': code,
        }
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://gaccounts.melon.com',
            'Referer': 'https://gaccounts.melon.com/ticketGlobal/authForJoin',
            'X-Requested-With': 'XMLHttpRequest'
        }
        response = self.session.post(url, headers=headers, data=data)
        print("[验证邮件验证码]: ", response.status_code)
        print("[验证邮件验证码]: ", response.text)
        res = response.json()
        if res:
            if res.get('serverToken'):
                self.server_token = res['serverToken']  # 更新实例中的token
                print("[验证邮件验证码]: 获取到的serverToken ", res['serverToken'])
                return res['serverToken']

        return None


    def join_completed(self, firstName: str, lastName: str, email: str, password: str, code: str, serverToken: str = None):
        """
        注册完成表单
        该表单字段都是通过aes非对称加密过后的
        :param firstName: 姓
        :param lastName: 名
        :param email: 邮箱
        :param password: 密码
        :param code: 验证码
        :param serverToken: serverToken，如果为None则使用实例中的token
        :return:
        """
        if serverToken is None:
            serverToken = self.server_token
            
        url = 'https://gaccounts.melon.com/ticketGlobal/joinCompleted'
        data = {
            'firstName': firstName,
            'lastName': lastName,
            'email': email,
            'password': password,
            'rePassword': password,
            'cpId': 'MP19',
            'lang': 'EN',
            'termsUserAgreement': 'Y',
            'termsPrivacyPolicy': 'Y',
            'termsOvsTransPInfo': 'Y',
            'redirectUrl': 'https://tkglobal.melon.com/main/index.htm?langCd=EN',
            'authKeyForJoin': code,
            'serverToken': serverToken
        }
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://gaccounts.melon.com',
            'Referer': 'https://gaccounts.melon.com/ticketGlobal/authForJoin',
        }
        response = self.session.post(url, headers=headers, data=data)
        print("[完成注册]: ", response.status_code)
        print("[完成注册]: ", response.text)
        return response.text


# 为了向后兼容，保留原有的独立函数
def melon_get_server_token():
    """
    请求获取join页面，然后从join页面中获取解析到serverToken
    :return: 返回serverToken
    """
    url = 'https://gaccounts.melon.com/ticketGlobal/join?cpId=MP19&lang=EN&redirectUrl=https%3A%2F%2Ftkglobal.melon.com%2Fmain%2Findex.htm%3FlangCd%3DEN'
    response = requests.get(url)
    pattern = r"joinForm\.append\(\$\('<input\/>'\, \{type: 'hidden', name: 'serverToken', value: \"([^\"]+)\" \}\)\);"
    match = re.search(pattern, response.text)
    if match:
        server_token = match.group(1)
        print("[获取serverToken]: ",server_token)
        return server_token


def melon_auth_for_join(firstName: str, lastName: str, email: str, password: str,serverToken: str):
    """
    melon平台注册验证表单请求
    表单信息是通过密钥加密后的
    :param firstName: 姓
    :param lastName: 名
    :param email: 邮箱
    :param password: 密码
    :param serverToken: serverToken
    :return:
    """
    url = 'https://gaccounts.melon.com/ticketGlobal/authForJoin'
    data = {
        'firstName': firstName,
        'lastName': lastName,
        'email': email,
        'password': password,
        'rePassword': password,
        'cpId': 'MP19',
        'lang': 'EN',
        'termsUserAgreement': 'Y',
        'termsPrivacyPolicy': 'Y',
        'termsOvsTransPInfo': 'Y',
        'redirectUrl': 'https://tkglobal.melon.com/main/index.htm?langCd=EN',
        'serverToken': serverToken
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://gaccounts.melon.com',
        'Referer': 'https://gaccounts.melon.com/ticketGlobal/join?cpId=MP19&lang=EN&redirectUrl=https%3A%2F%2Ftkglobal.melon.com%2Fmain%2Findex.htm%3FlangCd%3DEN',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    }
    response = requests.post(url, headers=headers, data=data)
    print("[提交注册申请表]: ",response.status_code)
    print("[提交注册申请表]: ",response.text)
    return response.text

def send_email_for_join(email:str):
    """
    发送验证码邮件
    :param email: 邮箱地址
    :return:
    """
    url = 'https://gaccounts.melon.com/ticketGlobal/reSendEmailForJoin'
    data = {
        'email': email,
    }

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Origin': 'https://gaccounts.melon.com',
        'Referer': 'https://gaccounts.melon.com/ticketGlobal/authForJoin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    response = requests.post(url, headers=headers, data=data)
    print("[发送邮件验证码]: ",response.status_code)
    print("[发送邮件验证码]: ",response.text)
    return response.text


def is_already_exist_email(email: str):
    """
    检查邮箱是否已经存在
    :param email: 邮箱
    :return: 如果存在就返回true，否则就返回false
    """
    url = 'https://gaccounts.melon.com/ticketGlobal/isAlreadyExistEmail'
    data = { 'email': email }
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://gaccounts.melon.com',
        'Referer': 'https://gaccounts.melon.com/ticketGlobal/authForJoin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    response = requests.post(url, headers=headers, data=data)
    print("[验证邮箱存在]",response.status_code)
    print("[验证邮箱存在]",response.text)
    res = response.json()
    if res is None:
        return False
    if res['isAlreadyExistEmail']:
        return True
    else:
        return False

def valid_auth_key_for_join(email: str,code:str):
    """
    验证邮件验证码，获取serverToken
    :param email: 邮箱
    :param code: 验证码
    :return:
    """
    url = 'https://gaccounts.melon.com/ticketGlobal/validAuthKeyForJoin'
    data = {
        'email': email,
        'authKey': code,
    }
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://gaccounts.melon.com',
        'Referer': 'https://gaccounts.melon.com/ticketGlobal/authForJoin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    response = requests.post(url,headers=headers,data=data)
    print("[验证邮件验证码]: ",response.status_code)
    print("[验证邮件验证码]: ",response.text)
    res = response.json()
    if res:
        if res['serverToken']:
            print("[验证邮件验证码]: 获取到的serverToken ",res['serverToken'])
            return res['serverToken']

    return None


def melon_join_completed(firstName: str, lastName: str, email: str, password: str, code: str, serverToken: str):
    """
    注册完成表单
    该表单字段都是通过aes非对称加密过后的
    :param firstName: 姓
    :param lastName: 名
    :param email: 邮箱
    :param password: 密码
    :param code: 验证吗
    :param serverToken: serverToken
    :return:
    """
    url = 'https://gaccounts.melon.com/ticketGlobal/joinCompleted'
    data = {
        'firstName': firstName,
        'lastName': lastName,
        'email': email,
        'password': password,
        'rePassword': password,
        'cpId': 'MP19',
        'lang': 'EN',
        'termsUserAgreement': 'Y',
        'termsPrivacyPolicy': 'Y',
        'termsOvsTransPInfo': 'Y',
        'redirectUrl': 'https://tkglobal.melon.com/main/index.htm?langCd=EN',
        'authKeyForJoin': code,
        'serverToken': serverToken
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://gaccounts.melon.com',
        'Referer': 'https://gaccounts.melon.com/ticketGlobal/authForJoin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    }
    response = requests.post(url,headers=headers,data=data)
    print("[完成注册]: ",response.status_code)
    print("[完成注册]: ",response.text)
    return response.text

# if __name__ == '__main__':
#     # email = '1437657457@qq.com'
#     email = '2180654922@qq.com'
#
#     # 1、提取serverToken
#     # serverToken = melon_get_server_token()
#
#     # 2、提交表单
#     # melon_auth_for_join("Fan","Zijian",email,'fhdsji43213hg21d',serverToken)
#     # 发送邮箱验证码
#     # send_email_for_join(email)
#
#     # 3、 获取邮件验证码
#     # 这里得通过操作邮箱从邮件中获取code
#     code:str = input().strip()
#
#     # 5、检查邮箱是否存在
#     if is_already_exist_email(email):
#         print("存在")
#     else:
#         print("不存在")
#
#     # 4、提交邮件验证码，验证验证码
#     serverToken = valid_auth_key_for_join(email,code)
#
#
#     # 6、完成注册
#     melon_join_completed("Test","User",email,"fds32d13f",code,serverToken)


# melon 平台注册接口封装
import re

import requests

def melon_get_server_token():
    """
    请求获取join页面，然后从join页面中获取解析到serverToken
    :return: 返回serverToken
    """
    url = 'https://gaccounts.melon.com/ticketGlobal/join?cpId=MP19&lang=EN&redirectUrl=https%3A%2F%2Ftkglobal.melon.com%2Fmain%2Findex.htm%3FlangCd%3DEN'
    response = requests.get(url)
    print(response.text)
    pattern = r"joinForm\.append\(\$\('<input\/>'\, \{type: 'hidden', name: 'serverToken', value: \"([^\"]+)\" \}\)\);"
    match = re.search(pattern, response.text)
    if match:
        server_token = match.group(1)
        print("提取到的serverToken",server_token)
        return server_token


def melon_auth_for_join(firstName: str, lastName: str, email: str, password: str,serverToken: str):
    """
    melon平台注册验证表单请求
    表单信息是通过密钥加密后的
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
    print(response.status_code)
    print(response.text)
    return response.text

def send_email_for_join(email:str):
    """
    发送验证码邮件
    :param email: 邮箱地址
    :return:
    """
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

def valid_auth_key_for_join():
    """
    验证邮件验证码
    :return:
    """

def is_already_exist_email():
    """
    检查邮箱是否已经存在
    :return:
    """

def melon_join_completed():
    """
    注册完成
    :return:
    """

if __name__ == '__main__':
    # 1、提取serverToken
    serverToken = melon_get_server_token()

    # 2、提交表单
    melon_auth_for_join("Fan","Zijian","2180654922@qq.com",'fhdsji43213hg21d',serverToken)

    # 3、 获取邮件验证码
    # 这里得通过操作邮箱从邮件中获取code

    # 4、提交邮件验证码，验证验证码
    valid_auth_key_for_join()
    # 5、检查邮箱是否存在
    is_already_exist_email()
    # 6、完成注册
    melon_join_completed()


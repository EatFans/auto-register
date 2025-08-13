# melon 平台注册接口封装
import re
from http.client import responses

import requests

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

def valid_auth_key_for_join():
    """
    验证邮件验证码
    :return:
    """


def melon_join_completed():
    """
    注册完成
    :return:
    """

if __name__ == '__main__':
    # email = '1437657457@qq.com'
    email = '2180654922@qq.com'

    # 1、提取serverToken
    # serverToken = melon_get_server_token()

    # 2、提交表单
    # melon_auth_for_join("Fan","Zijian",email,'fhdsji43213hg21d',serverToken)
    # 发送邮箱验证码
    # send_email_for_join(email)

    # 3、 获取邮件验证码
    # 这里得通过操作邮箱从邮件中获取code


    # 4、提交邮件验证码，验证验证码
    # valid_auth_key_for_join()
    # 5、检查邮箱是否存在
    if is_already_exist_email(email):
        print("存在")
    else:
        print("不存在")
    # 6、完成注册
    melon_join_completed()


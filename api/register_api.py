# 注册接口API封装
import requests

def verify_email_address(email):
    """
    验证邮箱地址接口
    :param email: 邮箱
    :return: 响应结果
    """
    url = "https://ticket.yes24.com/Pages/English/Member/Ajax/AjaxSignup.aspx"
    data = {
        'Email': email,
    }
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://ticket.yes24.com',
        'Referer': 'https://ticket.yes24.com/Pages/English/Member/FnSignUp.aspx',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    return requests.post(url, headers=headers, data=data)


def activation_email(email,k_token):
    """
    激活邮箱接口
    :param email: 邮箱
    :param k_token: 邮件中的token
    :return: 响应结果
    """
    url = 'https://ticket.yes24.com/Pages/English/member/FnMyAuthentication.aspx'
    params = {
        'k': k_token
    }
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://ticket.yes24.com',
        'Referer': 'https://ticket.yes24.com/Pages/English/Member/FnSignUp.aspx',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    return requests.get(url, headers=headers or {}, params=params)

def register(user):
    """
    注册接口
    :param user: 用户
    :return: 响应结果
    """

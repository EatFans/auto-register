import time

import requests
from api.register_api import *
from util.emai_util import *

def mailcow_create_mailbox(local_part, domain, password, api_url=None, api_key=None,
                           name="", quota="0", force_pw_update="0", tls_enforce_in="1", 
                           tls_enforce_out="1", tags=None):
    """
    使用 mailcow API 创建邮箱账号

    参数:
        local_part (str): 邮箱用户名（不包含@域名）
        domain (str): 邮箱域名
        password (str): 邮箱密码
        api_url (str): mailcow API 基础地址，例：https://mail.eatfan.top/api/v1
        api_key (str): mailcow API Key
        name (str): 邮箱持有者姓名，可空
        quota (str): 配额，单位MB，"0"表示无限
        force_pw_update (str): 是否强制用户首次登录后修改密码，"1"为是，"0"为否
        tls_enforce_in (str): 强制内部 TLS，"1"开启，"0"关闭
        tls_enforce_out (str): 强制外部 TLS，"1"开启，"0"关闭
        tags (list[str]): 邮箱标签列表，如 ["tag1","tag2"]

    返回:
        dict: API 返回的 JSON 结果
    """
    # 使用默认值如果没有提供配置
    if api_url is None:
        api_url = "http://127.0.0.1/api/v1"
    if api_key is None:
        api_key = "442317-C79337-D145B7-96DFC8-D2BF50"
    
    # 构建完整的API URL
    full_api_url = f"{api_url}/add/mailbox" if not api_url.endswith('/') else f"{api_url}add/mailbox"
    if tags is None:
        tags = []
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "active": "1",
        "domain": domain,
        "local_part": local_part,
        "name": name,
        "authsource": "mailcow",
        "password": password,
        "password2": password,
        "quota": quota,
        "force_pw_update": force_pw_update,
        "tls_enforce_in": tls_enforce_in,
        "tls_enforce_out": tls_enforce_out,
        "tags": tags
    }

    print(f"[Mailcow API] 创建邮箱请求:")
    print(f"URL: {full_api_url}")
    print(f"Headers: {headers}")
    print(f"Payload: {payload}")
    
    try:
        response = requests.post(full_api_url, headers=headers, json=payload)
        print(f"[Mailcow API] 响应状态码: {response.status_code}")
        print(f"[Mailcow API] 响应内容: {response.text}")
        response_data = response.json()
        
        # 添加HTTP状态码到响应中，便于调试
        if response.status_code != 200:
            response_data["http_status_code"] = response.status_code
            response_data["debug_info"] = {
                "api_url": full_api_url,
                "domain": domain,
                "local_part": local_part
            }
        
        return response_data
    except requests.exceptions.RequestException as e:
        print(f"[Mailcow API] 请求异常: {str(e)}")
        return {"error": f"请求失败: {str(e)}", "status_code": getattr(response, 'status_code', None)}
    except Exception as e:
        return {"error": f"解析响应失败: {str(e)}", "status_code": getattr(response, 'status_code', None), "text": getattr(response, 'text', None)}

def mailcow_delete_mailbox(email, api_url=None, api_key=None):
    """
    使用 mailcow API 删除邮箱账号

    参数:
        email (str): 要删除的邮箱地址
        api_url (str): mailcow API 基础地址
        api_key (str): mailcow API Key

    返回:
        dict: API 返回的 JSON 结果
    """
    # 使用默认值如果没有提供配置
    if api_url is None:
        api_url = "http://127.0.0.1/api/v1"
    if api_key is None:
        api_key = "442317-C79337-D145B7-96DFC8-D2BF50"
    
    # 构建完整的API URL
    full_api_url = f"{api_url}/delete/mailbox" if not api_url.endswith('/') else f"{api_url}delete/mailbox"
    
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = [email]  # mailcow API 通常接受邮箱地址列表

    print(f"[Mailcow API] 删除邮箱请求:")
    print(f"URL: {full_api_url}")
    print(f"Headers: {headers}")
    print(f"Payload: {payload}")
    
    response = requests.post(full_api_url, headers=headers, json=payload)
    print(f"[Mailcow API] 响应状态码: {response.status_code}")
    print(f"[Mailcow API] 响应内容: {response.text}")
    try:
        return response.json()
    except Exception as e:
        print(f"[Mailcow API] 请求异常: {str(e)}")
        return {"error": f"解析响应失败: {str(e)}", "status_code": response.status_code, "text": response.text}

def is_mailbox_created_successfully(api_response):
    """
    检查 Mailcow 创建邮箱 API 响应是否全部成功
    :param api_response: list[dict]，API返回的JSON
    :return: bool, True表示全部成功，False表示有失败
    """
    for item in api_response:
        if item.get("type") != "success":
            return False
    return True


# 临时邮箱API配置
TEMP_EMAIL_API_KEY = "9bf263b76bf1c46160182dba"

def generate_temp_email(domain="random", quantity=1):
    """
    生成临时邮箱地址
    
    参数:
        domain (str): 指定域名，"random"表示随机域名，也可以指定具体域名
        quantity (int): 生成数量，默认为1
    
    返回:
        dict: API返回的JSON结果
        {
            "mailbox": ["email1@domain.com", "email2@domain.com"],
            "quantity": 2,
            "status": 1
        }
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.linshiyouxiang.net/",
        "Origin": "https://www.linshiyouxiang.net"
    }
    url = f"https://www.linshiyouxiang.net/api_v1/email/mailbox?domain={domain}&quantity={quantity}"
    print(f"[临时邮箱API] 生成临时邮箱请求:")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"[临时邮箱API] 响应状态码: {response.status_code}")
        print(f"[临时邮箱API] 响应内容: {response.text}")
        response_data = response.json()
        # 只返回mailbox列表
        if response_data.get("status") == 1 and "mailbox" in response_data:
            return response_data["mailbox"]
        else:
            return []
    except Exception as e:
        print(f"获取临时邮箱失败: {str(e)}")
        return []

def read_email(email):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.linshiyouxiang.net/",
        "Origin": "https://www.linshiyouxiang.net"
    }
    read_url = f"https://www.linshiyouxiang.net/api_v1/email/readMessage?api_key={TEMP_EMAIL_API_KEY}&email={email}&sender_email=no-reply@yes24.com&time=PAST_1_HOUR&delete_after_read=false"
    print(f"[临时邮箱API] 读取邮件请求:")
    print(f"URL: {read_url}")
    print(f"Headers: {headers}")
    
    try:
        time.sleep(8)
        response = requests.get(read_url, headers=headers)
        print(f"[临时邮箱API] 响应状态码: {response.status_code}")
        print(f"[临时邮箱API] 响应内容: {response.text}")
        read_data = response.json()
        if 'id' in read_data:
            return read_data["content"]
    except Exception as e:
        print(f"读取邮件失败: {str(e)}")



if __name__ == "__main__":
    emails = generate_temp_email(quantity=1000)
    print(emails)
    # result = None
    # for email in emails:
    #     print(email) # 打印结果['avj0dhps@deepyinc.com']
    #
    #     verify_email_address(email)
    #
    #     result = read_email(email)
    #     print(result)
    #     k = extract_k_value(result)
    #     print(k)

    # 通过邮箱

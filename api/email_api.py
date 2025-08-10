import requests

def mailcow_create_mailbox(local_part, domain, password, name="", quota="0",
                           force_pw_update="0", tls_enforce_in="1", tls_enforce_out="1", tags=None):
    """
    使用 mailcow API 创建邮箱账号

    参数:
        api_url (str): mailcow API 基础地址，例：https://mail.eatfan.top/api/v1/add/mailbox
        api_key (str): mailcow API Key
        local_part (str): 邮箱用户名（不包含@域名）
        domain (str): 邮箱域名
        password (str): 邮箱密码
        name (str): 邮箱持有者姓名，可空
        quota (str): 配额，单位MB，"0"表示无限
        force_pw_update (str): 是否强制用户首次登录后修改密码，"1"为是，"0"为否
        tls_enforce_in (str): 强制内部 TLS，"1"开启，"0"关闭
        tls_enforce_out (str): 强制外部 TLS，"1"开启，"0"关闭
        tags (list[str]): 邮箱标签列表，如 ["tag1","tag2"]

    返回:
        dict: API 返回的 JSON 结果
    """
    API_URL = "http://127.0.0.1/api/v1/add/mailbox"
    API_KEY = "442317-C79337-D145B7-96DFC8-D2BF50"
    if tags is None:
        tags = []
    headers = {
        "X-API-Key": API_KEY,
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

    response = requests.post(API_URL, headers=headers, json=payload)
    try:
        return response.json()
    except Exception as e:
        return {"error": f"解析响应失败: {str(e)}", "status_code": response.status_code, "text": response.text}

def delet_email():
    API_URL = "http://127.0.0.1/api/v1/delete/email"


if __name__ == "__main__":

    res = mailcow_create_mailbox(
        local_part="TestUser",
        domain="eatfan.top",
        password="12345678",
        name="测试用户",
        quota="3072",
        force_pw_update="1",
        tags=["tag1", "tag2"]
    )
    print(res)
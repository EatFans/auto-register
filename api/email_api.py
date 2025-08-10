import requests

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

    try:
        response = requests.post(full_api_url, headers=headers, json=payload)
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

    response = requests.post(full_api_url, headers=headers, json=payload)
    try:
        return response.json()
    except Exception as e:
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

if __name__ == "__main__":
    # 测试创建邮箱
    res = mailcow_create_mailbox(
        local_part="TestUser2",
        domain="eatfan.top",
        password="12345678",
        api_url="http://127.0.0.1/api/v1",
        api_key="442317-C79337-D145B7-96DFC8-D2BF50",
        name="测试用户",
        quota="3072",
        force_pw_update="1",
        tags=["tag1", "tag2"]
    )
    print("创建邮箱结果:", res)
    
    # 测试删除邮箱
    # delete_res = mailcow_delete_mailbox(
    #     email="TestUser@eatfan.top",
    #     api_url="http://127.0.0.1/api/v1",
    #     api_key="442317-C79337-D145B7-96DFC8-D2BF50"
    # )
    # print("删除邮箱结果:", delete_res)
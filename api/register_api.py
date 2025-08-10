# 注册接口API封装
import requests
import json
import time
from typing import Optional, Dict, Any


class RegistrationSession:
    """
    注册会话管理类，统一管理注册流程中的会话状态
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.is_initialized = False
        self.email_verified = False
        self.email_activated = False
        self.form_accessed = False
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()
            
    def initialize_session(self) -> requests.Response:
        """
        初始化会话，访问注册页面获取初始Cookie
        :return: 响应结果
        """
        if self.is_initialized:
            return None
            
        url = "https://ticket.yes24.com/Pages/English/Member/FnSignUp.aspx"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        }
        response = self.session.get(url, headers=headers)
        self.is_initialized = True
        return response
        
    def get_session(self) -> requests.Session:
        """
        获取当前会话对象
        :return: requests.Session对象
        """
        if not self.is_initialized:
            self.initialize_session()
        return self.session
        
    def get_cookies_dict(self) -> Dict[str, str]:
        """
        获取当前会话的Cookie字典
        :return: Cookie字典
        """
        return dict(self.session.cookies)


def verify_email_address(email: str, session: Optional[requests.Session] = None) -> requests.Response:
    """
    验证邮箱地址接口
    :param email: 邮箱地址
    :param session: requests.Session对象，用于保持会话状态
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
    
    if session:
        return session.post(url, headers=headers, data=data)
    else:
        return requests.post(url, headers=headers, data=data)


def activation_email(email: str, k_token: str, session: Optional[requests.Session] = None) -> requests.Response:
    """
    激活邮箱接口
    :param email: 邮箱地址
    :param k_token: 激活令牌
    :param session: requests.Session对象，用于保持会话状态
    :return: 响应结果
    """
    url = "https://ticket.yes24.com/Pages/English/Member/FnMyAuthentication.aspx"
    params = {
        'k': k_token
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Referer': 'https://ticket.yes24.com/Pages/English/Member/FnSignUp.aspx'
    }
    
    if session:
        return session.get(url, headers=headers, params=params)
    else:
        return requests.get(url, headers=headers, params=params)


def register(email: str, password: str, surname: str, firstname: str, nation: int, birth: str, gender: str, session: Optional[requests.Session] = None) -> requests.Response:
    """
    注册接口
    :param email: 邮箱地址
    :param password: 密码
    :param surname: 姓氏
    :param firstname: 名字
    :param nation: 国家代码（数字）
    :param birth: 生日（YYYYMMDD格式）
    :param gender: 性别（m/f）
    :param session: requests.Session对象，用于保持会话状态
    :return: 响应结果
    """
    url = "https://ticket.yes24.com/Pages/English/Member/Ajax/AjaxSignupReg.aspx"

    # 构建请求数据
    data = {
        'Email': email,
        'Password': password,
        'Surname': surname,
        'Firstname': firstname,
        'Nation': str(nation),
        'Birth': birth,
        'Gender': gender,
        'ChkAgree': 'true',
        'ChkAgree2': 'true',
        'ChkOptionalAgree': 'true'
    }

    # 设置请求头
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://ticket.yes24.com',
        'Referer': 'https://ticket.yes24.com/Pages/English/Member/FnSignupReg.aspx',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    if session:
        return session.post(url, headers=headers, data=data)
    else:
        return requests.post(url, headers=headers, data=data)


def access_registration_form(session: Optional[requests.Session] = None) -> requests.Response:
    """
    访问注册表单页面，确保会话状态正确
    :param session: requests.Session对象，用于保持会话状态
    :return: 响应结果
    """
    url = "https://ticket.yes24.com/Pages/English/Member/FnSignupReg.aspx"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Referer': 'https://ticket.yes24.com/Pages/English/Member/FnSignUp.aspx'
    }
    
    if session:
        return session.get(url, headers=headers)
    else:
        return requests.get(url, headers=headers)


class RegistrationManager:
    """
    注册管理器，提供完整的注册流程管理
    """
    
    def __init__(self, reg_session: Optional[RegistrationSession] = None):
        self.reg_session = reg_session or RegistrationSession()
        self.own_session = reg_session is None
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.own_session:
            self.reg_session.close()
            
    def complete_registration(self, email: str, password: str, surname: str, firstname: str, 
                            nation: int, birth: str, gender: str, k_token: Optional[str] = None) -> Dict[str, Any]:
        """
        完整的注册流程
        :param email: 邮箱地址
        :param password: 密码
        :param surname: 姓氏
        :param firstname: 名字
        :param nation: 国家代码（数字）
        :param birth: 生日（YYYYMMDD格式）
        :param gender: 性别（m/f）
        :param k_token: 邮箱激活token（可选）
        :return: 注册结果字典
        """
        try:
            session = self.reg_session.get_session()
            results = {}
            
            # 步骤1: 初始化会话
            print("步骤1: 初始化会话")
            init_response = self.reg_session.initialize_session()
            if init_response:
                results['init_status'] = init_response.status_code
                print(f"会话初始化状态码: {init_response.status_code}")
            
            # 步骤2: 验证邮箱
            print(f"步骤2: 验证邮箱 {email}")
            verify_response = verify_email_address(email, session)
            results['verify_status'] = verify_response.status_code
            results['verify_result'] = verify_response.text
            print(f"邮箱验证结果: {verify_response.text}")
            
            # 检查邮箱验证结果
            try:
                verify_result = json.loads(verify_response.text)
                result_code = verify_result.get("ResultCode")
                if result_code not in ["00", "03"]:
                    return {"error": f"邮箱验证失败: {verify_result.get('ResultMsg', '未知错误')}"}
                self.reg_session.email_verified = True
                print(f"邮箱验证成功，ResultCode: {result_code}")
            except:
                print("邮箱验证响应解析失败，继续流程")
            
            # 步骤3: 邮箱激活（如果提供了k_token）
            if k_token:
                print(f"步骤3: 激活邮箱，使用token: {k_token}")
                activation_response = activation_email(email, k_token, session)
                results['activation_status'] = activation_response.status_code
                results['activation_result'] = activation_response.text
                print(f"邮箱激活状态码: {activation_response.status_code}")
                
                if "Authentication success" in activation_response.text:
                    print("邮箱激活成功")
                    self.reg_session.email_activated = True
                    time.sleep(1)  # 等待1秒
                else:
                    print("邮箱激活可能失败")
            else:
                print("步骤3: 未提供k_token，跳过邮箱激活")
                results['activation_result'] = "未提供k_token，跳过激活"
            
            # 步骤4: 访问注册表单页面
            print("步骤4: 访问注册表单页面")
            form_response = access_registration_form(session)
            results['form_status'] = form_response.status_code
            print(f"注册表单页面状态码: {form_response.status_code}")
            print(f"当前会话Cookies: {self.reg_session.get_cookies_dict()}")
            self.reg_session.form_accessed = True
            
            # 步骤5: 提交注册
            print(f"步骤5: 注册用户 {firstname} {surname}")
            time.sleep(1)  # 等待1秒再注册
            register_response = register(email, password, surname, firstname, nation, birth, gender, session)
            results['register_status'] = register_response.status_code
            results['register_result'] = register_response.text
            print(f"注册结果: {register_response.text}")
            
            # 判断注册是否成功
            success = "01" not in register_response.text or "Your information is not found" not in register_response.text
            results['success'] = success
            results['cookies'] = self.reg_session.get_cookies_dict()
            
            return results
            
        except Exception as e:
            return {"error": f"注册过程中发生错误: {str(e)}"}
    
    def verify_email_only(self, email: str) -> Dict[str, Any]:
        """
        仅验证邮箱
        :param email: 邮箱地址
        :return: 验证结果
        """
        session = self.reg_session.get_session()
        response = verify_email_address(email, session)
        self.reg_session.email_verified = True
        return {
            'status_code': response.status_code,
            'result': response.text,
            'cookies': self.reg_session.get_cookies_dict()
        }
    
    def activate_email_only(self, email: str, k_token: str) -> Dict[str, Any]:
        """
        仅激活邮箱
        :param email: 邮箱地址
        :param k_token: 激活token
        :return: 激活结果
        """
        session = self.reg_session.get_session()
        response = activation_email(email, k_token, session)
        if "Authentication success" in response.text:
            self.reg_session.email_activated = True
        return {
            'status_code': response.status_code,
            'result': response.text,
            'cookies': self.reg_session.get_cookies_dict()
        }
    
    def register_only(self, email: str, password: str, surname: str, firstname: str, 
                     nation: int, birth: str, gender: str) -> Dict[str, Any]:
        """
        仅提交注册
        :param email: 邮箱地址
        :param password: 密码
        :param surname: 姓氏
        :param firstname: 名字
        :param nation: 国家代码
        :param birth: 生日
        :param gender: 性别
        :return: 注册结果
        """
        session = self.reg_session.get_session()
        # 确保访问了注册表单页面
        if not self.reg_session.form_accessed:
            access_registration_form(session)
            self.reg_session.form_accessed = True
            
        response = register(email, password, surname, firstname, nation, birth, gender, session)
        return {
            'status_code': response.status_code,
            'result': response.text,
            'cookies': self.reg_session.get_cookies_dict()
        }



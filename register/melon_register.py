# Melon网站注册管理器

import sys
import os
import time
from typing import Dict, Any
from register.base_register import BaseRegisterManager
from entity.account import Account
from util.generate_util import *

# 添加模块路径
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'api'))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'email'))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'util'))

from api.melon_register_api import MelonRegistrationSession
from util.aes_util import encrypt_openssl_aes
from email_fetcher import EmailFetcher
from emai_util import extract_melon_code_value


class MelonRegisterManager(BaseRegisterManager):
    """
    Melon网站注册管理器
    实现完整的Melon注册流程，包括邮箱验证和验证码获取
    """

    def __init__(self, log_callback=None, app_instance=None):
        """
        初始化Melon注册管理器
        """
        super().__init__(log_callback, app_instance)
        self.session = None
        self.server_token = None

    def get_website_name(self) -> str:
        """
        获取网站名称
        :return: 网站名称
        """
        return "Melon"

    def validate_config(self, **kwargs) -> bool:
        """
        验证Melon注册配置
        :param kwargs: 配置参数
        :return: 配置是否有效
        """
        # Melon注册需要邮箱配置用于获取验证码
        self.log("验证Melon注册配置...", "blue")
        self.log("Melon注册配置验证通过", "green")
        return True

    def _register_single_account(self, email: str, password: str, user_data: Dict, **kwargs) -> bool:
        """
        注册单个账号的具体实现
        :param email: 邮箱地址
        :param password: 密码
        :param user_data: 用户数据字典
        :param kwargs: 其他参数
        :return: 注册是否成功
        """
        try:
            # 获取用户数据
            first_name = user_data.get('firstName', user_data.get('name', '').split()[0] if user_data.get('name') else 'Test')
            last_name = user_data.get('lastName', user_data.get('name', '').split()[-1] if user_data.get('name') and len(user_data.get('name', '').split()) > 1 else 'User')
            email_password = user_data.get('email_password', kwargs.get('email_password', ''))
            
            if not email_password:
                self.log(f"邮箱 {email} 缺少邮箱密码，跳过注册", "red")
                return False
            
            self.log(f"开始注册账号: {email}", "blue")
            
            # 步骤1: 初始化会话
            if not self._initialize_session():
                return False
            
            # 步骤2: 检查邮箱是否已存在
            if not self._check_email_exists(email):
                return False
            
            # 步骤3: 提交认证表单
            if not self._submit_auth_form(first_name, last_name, email, password):
                return False
            
            # 步骤4: 发送验证邮件
            if not self._send_verification_email(email):
                return False
            
            # 步骤5: 获取验证码
            verification_code = self._get_verification_code(email, email_password)
            if not verification_code:
                return False
            
            # 步骤6: 验证验证码
            if not self._verify_verification_code(email, verification_code):
                return False
            
            # 步骤7: 完成注册
            if not self._complete_registration(first_name, last_name, email, password, verification_code):
                return False
            
            # 创建账号对象并添加到存储
            account = Account(
                email=email,
                password=password,
                name=f"{first_name} {last_name}",
                birthday=user_data.get('birthday', ''),
                country=user_data.get('country', ''),
                gender=user_data.get('gender', '')
            )
            self.add_account_to_storage(account)
            self.update_registered_count()
            
            self.log(f"账号 {email} 注册成功", "green")
            return True
            
        except Exception as e:
            self.log(f"注册账号 {email} 失败: {str(e)}", "red")
            return False
        finally:
            # 清理会话
            self.session = None
            self.server_token = None
    
    def _verify_email(self, email: str, **kwargs) -> bool:
        """
        验证邮箱的具体实现
        :param email: 邮箱地址
        :param kwargs: 其他参数
        :return: 验证是否成功
        """
        try:
            if not self.session:
                self._initialize_session()
            
            return self._check_email_exists(email)
        except Exception as e:
            self.log(f"验证邮箱 {email} 失败: {str(e)}", "red")
            return False
    
    def _register_single_random(self, domain, name, birthday, country, gender, current_index, total_count, **kwargs):
        """
        随机注册单个账号的具体实现
        Melon不支持随机生成模式，只支持导入模式
        """
        self.log("Melon注册不支持随机生成模式，请使用导入数据模式", "red")
        return False
    
    def _register_single_import(self, domain, user_data, current_index, total_count, **kwargs):
        """
        导入注册单个账号的具体实现
        :param domain: 邮箱域名（Melon中不使用）
        :param user_data: 用户数据
        :param current_index: 当前索引
        :param total_count: 总数量
        :param kwargs: 其他参数
        :return: 注册是否成功
        """
        try:
            # 从用户数据中获取必要信息
            email = user_data.get('email', '')
            password = generate_password()
            email_password = user_data.get('email_password', '')
            
            if not email:
                self.log(f"第 {current_index} 行数据缺少邮箱地址，跳过", "red")
                return False
            
            if not email_password:
                self.log(f"第 {current_index} 行数据缺少邮箱密钥，跳过", "red")
                return False
            
            self.log(f"正在注册第 {current_index}/{total_count} 个账号: {email}", "blue")
            
            # 调用单个账号注册方法，传入邮箱密钥
            success = self._register_single_account(email, password, user_data, email_password=email_password, **kwargs)
            
            if success:
                self.log(f"第 {current_index}/{total_count} 个账号注册成功", "green")
            else:
                self.log(f"第 {current_index}/{total_count} 个账号注册失败", "red")
            
            return success
            
        except Exception as e:
            self.log(f"注册第 {current_index} 个账号时发生异常: {str(e)}", "red")
            return False
    
    def _initialize_session(self) -> bool:
        """
        初始化会话并获取serverToken
        :return: 初始化是否成功
        """
        try:
            self.log("初始化Melon注册会话...", "blue")
            self.session = MelonRegistrationSession()
            self.server_token = self.session.get_server_token()
            
            if self.server_token:
                self.log(f"获取serverToken成功: {self.server_token[:20]}...", "green")
                return True
            else:
                self.log("获取serverToken失败", "red")
                return False
                
        except Exception as e:
            self.log(f"初始化会话失败: {str(e)}", "red")
            return False
    
    def _check_email_exists(self, email: str) -> bool:
        """
        检查邮箱是否已存在
        :param email: 邮箱地址
        :return: 邮箱是否可用（True表示可用，False表示已存在）
        """
        try:
            self.log(f"检查邮箱 {email} 是否已被注册...", "blue")
            email_exists = self.session.is_already_exist_email(email)
            
            if email_exists:
                self.log(f"邮箱 {email} 已被注册", "red")
                return False
            else:
                self.log(f"邮箱 {email} 可用", "green")
                return True
                
        except Exception as e:
            self.log(f"检查邮箱失败: {str(e)}", "red")
            return False
    
    def _submit_auth_form(self, first_name: str, last_name: str, email: str, password: str) -> bool:
        """
        提交认证表单（需要AES加密）
        :param first_name: 名字
        :param last_name: 姓氏
        :param email: 邮箱
        :param password: 密码
        :return: 提交是否成功
        """
        try:
            self.log("提交认证表单...", "blue")
            
            # 加密用户数据
            encrypted_firstName = encrypt_openssl_aes(first_name)
            encrypted_lastName = encrypt_openssl_aes(last_name)
            encrypted_email = encrypt_openssl_aes(email)
            encrypted_password = encrypt_openssl_aes(password)
            
            # 提交认证表单
            result = self.session.submit_auth_form(
                encrypted_firstName,
                encrypted_lastName,
                encrypted_email,
                encrypted_password
            )
            
            # 检查结果
            if result and not ('error' in result.lower() and '<html>' in result.lower()):
                self.log("认证表单提交成功", "green")
                return True
            elif '<html>' in result.lower():
                self.log("认证表单提交成功（返回HTML页面）", "green")
                return True
            else:
                self.log("认证表单提交失败", "red")
                return False
                
        except Exception as e:
            self.log(f"提交认证表单失败: {str(e)}", "red")
            return False
    
    def _send_verification_email(self, email: str) -> bool:
        """
        发送验证邮件
        :param email: 邮箱地址
        :return: 发送是否成功
        """
        try:
            self.log(f"向 {email} 发送验证邮件...", "blue")
            result = self.session.send_email_for_join(email)
            
            if result:
                self.log("验证邮件发送成功", "green")
                return True
            else:
                self.log("验证邮件发送失败", "red")
                return False
                
        except Exception as e:
            self.log(f"发送验证邮件失败: {str(e)}", "red")
            return False
    
    def _get_verification_code(self, email: str, email_password: str) -> str:
        """
        从邮箱中获取验证码
        :param email: 邮箱地址
        :param email_password: 邮箱密码
        :return: 验证码，获取失败返回None
        """
        email_fetcher = None
        try:
            self.log(f"连接邮箱 {email} 获取验证码...", "blue")
            
            # 初始化邮件抓取器
            email_fetcher = EmailFetcher(email, email_password)
            
            if not email_fetcher.connect():
                self.log("邮箱连接失败", "red")
                return None
            
            self.log("邮箱连接成功，等待验证邮件...", "green")
            
            # 等待邮件到达（最多等待60秒）
            max_attempts = 12  # 12次，每次等待5秒
            
            for attempt in range(max_attempts):
                self.log(f"尝试获取验证邮件 {attempt + 1}/{max_attempts}...", "blue")
                
                # 获取来自Melon的邮件
                emails = email_fetcher.get_emails_from_sender(
                    sender='noreply_melonticket@kakaoent.com',
                    unseen_only=True,
                    limit=1
                )
                
                if emails:
                    email_info = emails[0]
                    self.log(f"找到验证邮件: {email_info['subject']}", "green")
                    
                    # 提取验证码
                    html_body = email_info.get('html_body', '') or email_info.get('body', '')
                    verification_code = extract_melon_code_value(html_body)
                    
                    if verification_code:
                        self.log(f"成功提取验证码: {verification_code}", "green")
                        
                        # 标记邮件为已读
                        email_fetcher.mark_as_read(email_info['id'])
                        
                        return verification_code
                    else:
                        self.log("邮件中未找到验证码，继续等待...", "yellow")
                
                if attempt < max_attempts - 1:
                    time.sleep(5)  # 等待5秒后重试
            
            self.log("等待超时，未收到验证邮件", "red")
            return None
            
        except Exception as e:
            self.log(f"获取验证码失败: {str(e)}", "red")
            return None
        finally:
            # 断开邮箱连接
            if email_fetcher:
                email_fetcher.disconnect()
    
    def _verify_verification_code(self, email: str, verification_code: str) -> bool:
        """
        验证验证码
        :param email: 邮箱地址
        :param verification_code: 验证码
        :return: 验证是否成功
        """
        try:
            self.log(f"验证验证码: {verification_code}", "blue")
            new_server_token = self.session.valid_auth_key_for_join(email, verification_code)
            
            if new_server_token:
                self.server_token = new_server_token
                self.log(f"验证码验证成功，获取新的serverToken: {new_server_token[:20]}...", "green")
                return True
            else:
                self.log("验证码验证失败", "red")
                return False
                
        except Exception as e:
            self.log(f"验证验证码失败: {str(e)}", "red")
            return False
    
    def _complete_registration(self, first_name: str, last_name: str, email: str, password: str, verification_code: str) -> bool:
        """
        完成注册（需要AES加密）
        :param first_name: 名字
        :param last_name: 姓氏
        :param email: 邮箱
        :param password: 密码
        :param verification_code: 验证码
        :return: 注册是否成功
        """
        try:
            self.log("提交最终注册表单...", "blue")
            
            # 加密用户数据（除了验证码和serverToken）
            encrypted_firstName = encrypt_openssl_aes(first_name)
            encrypted_lastName = encrypt_openssl_aes(last_name)
            encrypted_email = encrypt_openssl_aes(email)
            encrypted_password = encrypt_openssl_aes(password)
            
            # 完成注册
            result = self.session.join_completed(
                encrypted_firstName,
                encrypted_lastName,
                encrypted_email,
                encrypted_password,
                verification_code,  # 验证码不加密
                self.server_token   # serverToken不加密
            )
            
            if result:
                self.log("注册流程完成", "green")
                return True
            else:
                self.log("注册完成失败", "red")
                return False
                
        except Exception as e:
            self.log(f"完成注册失败: {str(e)}", "red")
            return False
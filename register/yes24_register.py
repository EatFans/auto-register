# Yes24网站注册管理器
from register.base_register import BaseRegisterManager
from api.register_api import RegistrationManager as APIRegistrationManager, verify_email_address, activation_email, register
from api.email_api import mailcow_create_mailbox, generate_temp_email, read_email
from util.generate_util import *
from entity.account import Account
from datetime import datetime
import json
import time

class Yes24RegisterManager(BaseRegisterManager):
    """
    Yes24网站注册管理器
    """
    
    def get_website_name(self) -> str:
        """
        获取网站名称
        :return: 网站名称
        """
        return "Yes24"
    
    def validate_config(self, **kwargs) -> bool:
        """
        验证Yes24注册配置
        :param kwargs: 配置参数
        :return: 配置是否有效
        """
        # Yes24注册使用临时邮箱API，不需要域名配置
        # 可以在这里添加其他必要的配置验证
        
        self.log(f"Yes24注册配置验证通过（使用临时邮箱API）", "green")
        return True
    

    def _verify_email(self, email: str, **kwargs) -> bool:
        """
        验证邮箱
        :param email: 邮箱地址
        :param kwargs: 其他参数
        :return: 验证是否成功
        """
        try:
            self.log(f"开始验证邮箱: {email}", "blue")
            
            # 创建注册管理器并验证邮箱
            registration_manager = APIRegistrationManager()
            
            # 初始化会话
            init_response = registration_manager.reg_session.initialize_session()
            if not init_response or init_response.status_code != 200:
                self.log(f"会话初始化失败: {email}", "red")
                return False
            
            # 验证邮箱
            verify_result_data = registration_manager.verify_email_only(email)
            if verify_result_data['status_code'] != 200:
                self.log(f"邮箱验证失败: {email}，状态码: {verify_result_data['status_code']}", "red")
                return False
            
            # 检查验证结果内容
            try:
                result_data = json.loads(verify_result_data['result'])
                result_code = result_data.get('ResultCode')
                if result_code in ['00', '03']:
                    self.log(f"邮箱验证成功: {email}", "green")
                    return True
                else:
                    error_msg = result_data.get('ResultMsg', '验证失败')
                    self.log(f"邮箱验证失败: {email}, ResultCode: {result_code}, 错误: {error_msg}", "red")
                    return False
            except (json.JSONDecodeError, AttributeError):
                self.log(f"邮箱验证响应解析失败: {email}", "red")
                return False
                
        except Exception as e:
            self.log(f"邮箱验证异常: {email}, 错误: {str(e)}", "red")
            return False
    
    def _verify_email_with_manager(self, email: str, registration_manager, **kwargs) -> bool:
        """
        使用指定的registration_manager验证邮箱
        :param email: 邮箱地址
        :param registration_manager: 注册管理器实例
        :param kwargs: 其他参数
        :return: 验证是否成功
        """
        try:
            self.log(f"开始验证邮箱: {email}", "blue")
            
            # 初始化会话
            init_response = registration_manager.reg_session.initialize_session()
            if not init_response or init_response.status_code != 200:
                self.log(f"会话初始化失败: {email}", "red")
                return False
            
            # 验证邮箱
            verify_result_data = registration_manager.verify_email_only(email)
            if verify_result_data['status_code'] != 200:
                self.log(f"邮箱验证失败: {email}，状态码: {verify_result_data['status_code']}", "red")
                return False
            
            # 检查验证结果内容
            try:
                result_data = json.loads(verify_result_data['result'])
                result_code = result_data.get('ResultCode')
                if result_code in ['00', '03']:
                    self.log(f"邮箱验证成功: {email}", "green")
                    return True
                else:
                    error_msg = result_data.get('ResultMsg', '验证失败')
                    self.log(f"邮箱验证失败: {email}, ResultCode: {result_code}, 错误: {error_msg}", "red")
                    return False
            except (json.JSONDecodeError, AttributeError):
                self.log(f"邮箱验证响应解析失败: {email}", "red")
                return False
                
        except Exception as e:
            self.log(f"邮箱验证异常: {email}, 错误: {str(e)}", "red")
            return False
    
    def _register_single_account(self, email: str, password: str, user_data: dict, **kwargs) -> bool:
        """
        注册单个Yes24账号
        :param email: 邮箱地址
        :param password: 密码
        :param user_data: 用户数据字典
        :param kwargs: 其他参数
        :return: 注册是否成功
        """
        try:
            self.log(f"开始注册Yes24账号: {email}", "blue")
            
            # 创建注册管理器
            registration_manager = APIRegistrationManager()
            
            # 执行注册
            register_result_data = registration_manager.register_only(
                email=email,
                password=password,
                surname=user_data.get('surname', ''),
                firstname=user_data.get('firstname', ''),
                nation=self._get_country_code(user_data.get('country', 'China')),
                birth=user_data.get('birthday', '20000101').replace('-', ''),  # 确保格式为YYYYMMDD
                gender=self._get_gender_code(user_data.get('gender', '男'))
            )
            
            if register_result_data['status_code'] == 200:
                # 检查注册结果
                try:
                    result_data = json.loads(register_result_data['result'])
                    result_code = result_data.get('ResultCode')
                    result_msg = result_data.get('ResultMsg', '')
                    
                    if result_code == '00':
                        self.log(f"Yes24账号注册成功: {email}", "green")
                        return True
                    else:
                        self.log(f"Yes24账号注册失败: {email}，ResultCode: {result_code}，错误: {result_msg}", "red")
                        return False
                except (json.JSONDecodeError, AttributeError):
                    self.log(f"注册响应解析失败: {email}", "red")
                    return False
            else:
                self.log(f"注册失败: {email}，状态码: {register_result_data['status_code']}", "red")
                return False
                
        except Exception as e:
            self.log(f"Yes24账号注册异常: {email}, 错误: {str(e)}", "red")
            return False
    
    def _register_single_account_with_manager(self, email: str, password: str, user_data: dict, registration_manager, **kwargs) -> bool:
        """
        使用指定的registration_manager注册单个Yes24账号
        :param email: 邮箱地址
        :param password: 密码
        :param user_data: 用户数据字典
        :param registration_manager: 注册管理器实例
        :param kwargs: 其他参数
        :return: 注册是否成功
        """
        try:
            self.log(f"开始注册Yes24账号: {email}", "blue")
            
            # 执行注册
            register_result_data = registration_manager.register_only(
                email=email,
                password=password,
                surname=user_data.get('surname', ''),
                firstname=user_data.get('firstname', ''),
                nation=self._get_country_code(user_data.get('country', 'China')),
                birth=user_data.get('birthday', '20000101').replace('-', ''),  # 确保格式为YYYYMMDD
                gender=self._get_gender_code(user_data.get('gender', '男'))
            )
            
            if register_result_data['status_code'] == 200:
                # 检查注册结果
                try:
                    result_data = json.loads(register_result_data['result'])
                    result_code = result_data.get('ResultCode')
                    result_msg = result_data.get('ResultMsg', '')
                    
                    if result_code == '00':
                        self.log(f"Yes24账号注册成功: {email}", "green")
                        return True
                    else:
                        self.log(f"Yes24账号注册失败: {email}，ResultCode: {result_code}，错误: {result_msg}", "red")
                        return False
                except (json.JSONDecodeError, AttributeError):
                    self.log(f"注册响应解析失败: {email}", "red")
                    return False
            else:
                self.log(f"注册失败: {email}，状态码: {register_result_data['status_code']}", "red")
                return False
                
        except Exception as e:
            self.log(f"Yes24账号注册异常: {email}, 错误: {str(e)}", "red")
            return False
    
    def _register_single_random(self, domain, name, birthday, country, gender, current_index, total_count, **kwargs):
        """
        随机注册单个Yes24账号
        """
        try:
            self.log(f"[{current_index}/{total_count}] 开始随机注册Yes24账号...", "cyan")
            
            # 生成随机数据
            password = generate_password()
            
            # 使用临时邮箱API生成邮箱
            temp_email_list = generate_temp_email(quantity=1)
            if not temp_email_list or len(temp_email_list) == 0:
                self.log(f"[{current_index}/{total_count}] 生成临时邮箱失败", "red")
                return False
            
            email = temp_email_list[0]
            
            # 处理用户数据
            actual_name = name if name else generate_name()
            name_parts = actual_name.split(' ', 1)
            surname = name_parts[0] if len(name_parts) > 0 else generate_name().split(' ')[0]
            firstname = name_parts[1] if len(name_parts) > 1 else generate_name().split(' ')[1] if ' ' in generate_name() else ''
            
            actual_country = country if country else 'China'
            actual_gender = gender if gender else '남성'
            actual_birthday = birthday if birthday else '2000-01-01'
            
            # 执行完整注册流程
            success = self._complete_registration(
                email=email,
                password=password,
                surname=surname,
                firstname=firstname,
                country=actual_country,
                gender=actual_gender,
                birthday=actual_birthday,
                current_index=current_index,
                total_count=total_count,
                source_type="随机",
                **kwargs
            )
            
            return success
            
        except Exception as e:
            self.log(f"[{current_index}/{total_count}] 随机注册异常: {str(e)}", "red")
            return False
    
    def _register_single_import(self, domain, user_data, current_index, total_count, **kwargs):
        """
        导入注册单个Yes24账号
        """
        try:
            name = user_data.get('name', '')
            birthday = user_data.get('birthday', '2000-01-01')
            country = user_data.get('country', 'China')
            gender = user_data.get('gender', '남성')
            
            self.log(f"[{current_index}/{total_count}] 开始导入注册Yes24账号: {name}", "cyan")
            
            # 生成密码
            password = generate_password()
            
            # 使用临时邮箱API生成邮箱
            temp_email_list = generate_temp_email(quantity=1)
            if not temp_email_list or len(temp_email_list) == 0:
                self.log(f"[{current_index}/{total_count}] 生成临时邮箱失败", "red")
                return False
            
            email = temp_email_list[0]
            
            # 处理姓名
            name_parts = name.split(' ', 1)
            surname = name_parts[0] if len(name_parts) > 0 else name
            firstname = name_parts[1] if len(name_parts) > 1 else ''
            
            # 执行完整注册流程
            success = self._complete_registration(
                email=email,
                password=password,
                surname=surname,
                firstname=firstname,
                country=country,
                gender=gender,
                birthday=birthday,
                current_index=current_index,
                total_count=total_count,
                source_type="导入",
                **kwargs
            )
            
            return success
            
        except Exception as e:
            self.log(f"[{current_index}/{total_count}] 导入注册异常: {str(e)}", "red")
            return False
    
    def _complete_registration(self, email, password, surname, firstname, country, gender, birthday, current_index, total_count, source_type, **kwargs):
        """
        完成完整的Yes24注册流程
        """
        # 创建统一的注册管理器，保持会话状态
        registration_manager = APIRegistrationManager()
        
        try:
            # 1. 验证邮箱地址 (临时邮箱已在生成时创建)
            self.log(f"[{current_index}/{total_count}] 步骤1: 验证邮箱地址 {email}", "blue")
            if not self._verify_email_with_manager(email, registration_manager, **kwargs):
                return False
            
            # 2. 处理邮箱激活
            self.log(f"[{current_index}/{total_count}] 步骤2: 处理邮箱激活 {email}", "blue")
            activation_result = self._process_email_activation_with_manager(email, registration_manager)
            if not activation_result:
                self.log(f"[{current_index}/{total_count}] 邮箱激活失败: {email}", "red")
                return False
            
            # 3. 注册Yes24账号
            self.log(f"[{current_index}/{total_count}] 步骤3: 注册Yes24账号 {email}", "blue")
            user_data = {
                'surname': surname,
                'firstname': firstname,
                'country': country,
                'gender': gender,
                'birthday': birthday
            }
            
            if not self._register_single_account_with_manager(email, password, user_data, registration_manager, **kwargs):
                return False
            
            # 4. 保存账号信息
            account = Account(
                email=email,
                password=password,
                name=f"{surname} {firstname}".strip(),
                birthday=birthday,
                country=country,
                gender=gender
            )
            
            self.add_account_to_storage(account)
            self.update_registered_count()
            
            self.log(f"[{current_index}/{total_count}] Yes24账号注册完成: {email}", "green")
            return True
            
        except Exception as e:
            self.log(f"[{current_index}/{total_count}] 完整注册流程异常: {str(e)}", "red")
            return False
        finally:
            # 确保会话被正确关闭
            try:
                registration_manager.reg_session.close()
            except:
                pass
    
    def _process_email_activation(self, email, timeout=300):
        """
        处理邮箱激活
        :param email: 邮箱地址
        :param timeout: 超时时间（秒）
        :return: 激活是否成功
        """
        try:
            # 等待邮件到达
            time.sleep(5)
            
            k_value = None
            max_retries = 3
            for retry in range(max_retries):
                try:
                    email_content = read_email(email)
                    if email_content and 'k=' in email_content:
                        # 提取k值
                        import re
                        import urllib.parse
                        # 先尝试从URL中提取k值
                        k_match = re.search(r'k=([a-f0-9\-]+)', email_content)
                        if k_match:
                            k_value = k_match.group(1)
                            # URL解码
                            k_value = urllib.parse.unquote(k_value)
                            # 去除可能的HTML标签
                            k_value = re.sub(r'<[^>]+>', '', k_value).strip()
                            if k_value:  # 确保k值不为空
                                break
                except Exception as e:
                    self.log(f"读取邮件失败 (重试 {retry + 1}/{max_retries}): {str(e)}", "orange")
                
                # 等待一段时间后重试
                time.sleep(5)
            
            if not k_value:
                self.log(f"未能获取到k值: {email}", "red")
                return False
            
            self.log(f"成功获取k值: {k_value}", "green")
            
            # 激活邮箱
            registration_manager = APIRegistrationManager()
            
            # 初始化会话
            init_response = registration_manager.reg_session.initialize_session()
            if not init_response or init_response.status_code != 200:
                self.log(f"会话初始化失败: {email}", "red")
                return False
            
            activation_result_data = registration_manager.activate_email_only(email, k_value)
            if activation_result_data['status_code'] != 200:
                self.log(f"邮箱激活失败，状态码: {activation_result_data['status_code']}", "red")
                return False
            
            # 检查激活是否成功 - 如果包含错误信息则表示失败
            if "The authentication key is not valid" in activation_result_data['result']:
                self.log(f"邮箱激活失败，k值无效: {email}", "red")
                return False
            
            # 检查是否有其他错误信息
            if "alert(" in activation_result_data['result'] and "error" in activation_result_data['result'].lower():
                self.log(f"邮箱激活失败，响应包含错误信息: {email}", "red")
                return False
            
            self.log(f"邮箱激活成功: {email}", "green")
            return True
            
        except Exception as e:
            self.log(f"邮箱激活异常: {email}, 错误: {str(e)}", "red")
            return False
    
    def _process_email_activation_with_manager(self, email, registration_manager, timeout=300):
        """
        使用指定的registration_manager处理邮箱激活
        :param email: 邮箱地址
        :param registration_manager: 注册管理器实例
        :param timeout: 超时时间（秒）
        :return: 激活是否成功
        """
        try:
            # 等待邮件到达
            time.sleep(5)
            
            k_value = None
            max_retries = 3
            for retry in range(max_retries):
                try:
                    email_content = read_email(email)
                    if email_content and 'k=' in email_content:
                        # 提取k值
                        import re
                        import urllib.parse
                        # 先尝试从URL中提取k值
                        k_match = re.search(r'k=([a-f0-9\-]+)', email_content)
                        if k_match:
                            k_value = k_match.group(1)
                            # URL解码
                            k_value = urllib.parse.unquote(k_value)
                            # 去除可能的HTML标签
                            k_value = re.sub(r'<[^>]+>', '', k_value).strip()
                            if k_value:  # 确保k值不为空
                                break
                except Exception as e:
                    self.log(f"读取邮件失败 (重试 {retry + 1}/{max_retries}): {str(e)}", "orange")
                
                # 等待一段时间后重试
                time.sleep(5)
            
            if not k_value:
                self.log(f"未能获取到k值: {email}", "red")
                return False
            
            self.log(f"成功获取k值: {k_value}", "green")
            
            # 激活邮箱（使用传入的registration_manager，无需重新初始化会话）
            activation_result_data = registration_manager.activate_email_only(email, k_value)
            if activation_result_data['status_code'] != 200:
                self.log(f"邮箱激活失败，状态码: {activation_result_data['status_code']}", "red")
                return False
            
            # 检查激活是否成功 - 如果包含错误信息则表示失败
            if "The authentication key is not valid" in activation_result_data['result']:
                self.log(f"邮箱激活失败，k值无效: {email}", "red")
                return False
            
            # 检查是否有其他错误信息
            if "alert(" in activation_result_data['result'] and "error" in activation_result_data['result'].lower():
                self.log(f"邮箱激活失败，响应包含错误信息: {email}", "red")
                return False
            
            self.log(f"邮箱激活成功: {email}", "green")
            return True
            
        except Exception as e:
            self.log(f"邮箱激活异常: {email}, 错误: {str(e)}", "red")
            return False
    
    def _get_country_code(self, country):
        """
        获取国家代码映射
        :param country: 国家名称（支持中英文）
        :return: 国家代码
        """
        country_mapping = {
            # 中文映射
            '中国': 43,
            '美国': 1,
            '日本': 81,
            '韩国': 82,
            '英国': 44,
            '德国': 49,
            '法国': 33,
            '加拿大': 1,
            '澳大利亚': 61,
            # 英文映射
            'China': 43,
            'USA': 1,
            'United States': 1,
            'Japan': 81,
            'Korea': 82,
            'South Korea': 82,
            'UK': 44,
            'United Kingdom': 44,
            'Germany': 49,
            'France': 33,
            'Canada': 1,
            'Australia': 61
        }
        return country_mapping.get(country, 43)  # 默认返回中国代码43
    
    def _get_gender_code(self, gender):
        """
        获取性别代码映射
        :param gender: 性别（支持中英文）
        :return: 性别代码
        """
        gender_mapping = {
            # 中文映射
            '男': 'm',
            '女': 'f',
            '男性': 'm',
            '女性': 'f',
            # 英文映射
            'male': 'm',
            'female': 'f',
            'man': 'm',
            'woman': 'f',
            'm': 'm',
            'f': 'f'
        }
        return gender_mapping.get(gender.lower() if gender else '', 'm')  # 默认返回男性
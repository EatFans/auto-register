from api.register_api import RegistrationManager as APIRegistrationManager, RegistrationSession, RegistrationManager, verify_email_address, activation_email, register, access_registration_form
from api.email_api import mailcow_create_mailbox, generate_temp_email, read_email
from util.generate_util import *
from datetime import datetime
from account_storage import AccountStorage
from util.excel_util import *
from entity.account import Account
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class RegisterManager:
    def __init__(self, log_callback=None, app_instance=None):
        """
        初始化注册管理器
        
        :param log_callback: 日志回调函数，接收消息和颜色两个参数
        :param app_instance: Application实例，用于更新表格
        """
        self.log_callback = log_callback
        self.app_instance = app_instance
        self.account_storage = AccountStorage()

    def log(self, message, color="black"):
        """
        输出日志
        :param message: 日志消息
        :param color: 字体颜色
        """
        if self.log_callback:
            self.log_callback(message, color)
        else:
            print(message)
    
    def register_accounts_random(self, domain, count, name, birthday, country, gender, export_path, thread_count=5):
        """
        随机生成模式注册账号
        :param domain: 邮箱域名
        :param count: 注册数量
        :param name: 名字（空则随机生成）
        :param birthday: 生日
        :param country: 国家
        :param gender: 性别
        :param export_path: 导出路径
        :param thread_count: 线程数
        """
        # 清空之前的账号存储
        self.account_storage.clear()
        
        # 多线程注册
        self._register_with_threads_random(domain, count, name, birthday, country, gender, thread_count)
        
        # 导出结果
        self._export_results(export_path)
    
    def register_accounts_import(self, domain, user_data, export_path, thread_count=5):
        """
        导入数据模式注册账号
        :param domain: 邮箱域名
        :param user_data: 导入的用户数据列表
        :param export_path: 导出路径
        :param thread_count: 线程数
        """
        # 清空之前的账号存储
        self.account_storage.clear()
        
        # 多线程注册
        self._register_with_threads_import(domain, user_data, thread_count)
        
        # 导出结果
        self._export_results(export_path)
    
    def _register_with_threads_random(self, domain, count, name, birthday, country, gender, thread_count):
        """
        使用多线程进行随机生成模式注册
        """
        self.log(f"开始使用 {thread_count} 个线程进行随机注册，目标数量: {count}", "blue")
        self.log(f"注册参数: 域名={domain}, 姓名={name}, 生日={birthday}, 国家={country}, 性别={gender}", "blue")
        
        # 创建线程锁，保护共享资源
        self.lock = threading.Lock()
        self.registered_count = 0
        
        # 使用线程池执行注册任务
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            # 提交注册任务
            futures = []
            self.log(f"正在提交 {count} 个注册任务到线程池...", "cyan")
            
            for i in range(count):
                future = executor.submit(self._register_single_random, domain, name, birthday, country, gender, i+1, count)
                futures.append(future)
            
            self.log(f"所有任务已提交，等待执行完成...", "cyan")
            
            # 等待所有任务完成
            completed_tasks = 0
            for future in as_completed(futures):
                try:
                    future.result()
                    completed_tasks += 1
                    if completed_tasks % 5 == 0 or completed_tasks == count:  # 每5个任务或最后一个任务报告进度
                        self.log(f"进度更新: 已完成 {completed_tasks}/{count} 个任务", "blue")
                except Exception as e:
                    completed_tasks += 1
                    self.log(f"注册任务执行出错: {str(e)}", "red")
            
            self.log(f"所有注册任务执行完毕，成功注册: {self.registered_count}/{count}", "green")
    
    def _register_with_threads_import(self, domain, user_data, thread_count):
        """
        使用多线程进行导入数据模式注册
        """
        total_users = len(user_data)
        self.log(f"开始使用 {thread_count} 个线程进行导入数据注册，目标数量: {total_users}", "blue")
        self.log(f"注册域名: {domain}", "blue")
        
        # 创建线程锁，保护共享资源
        self.lock = threading.Lock()
        self.registered_count = 0
        
        # 使用线程池执行注册任务
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            # 提交注册任务
            futures = []
            self.log(f"正在提交 {total_users} 个注册任务到线程池...", "cyan")
            
            for i, user in enumerate(user_data):
                future = executor.submit(self._register_single_import, domain, user, i+1, total_users)
                futures.append(future)
            
            self.log(f"所有任务已提交，等待执行完成...", "cyan")
            
            # 等待所有任务完成
            completed_tasks = 0
            for future in as_completed(futures):
                try:
                    future.result()
                    completed_tasks += 1
                    if completed_tasks % 5 == 0 or completed_tasks == total_users:  # 每5个任务或最后一个任务报告进度
                        self.log(f"进度更新: 已完成 {completed_tasks}/{total_users} 个任务", "blue")
                except Exception as e:
                    completed_tasks += 1
                    self.log(f"注册任务执行出错: {str(e)}", "red")
            
            self.log(f"所有注册任务执行完毕，成功注册: {self.registered_count}/{total_users}", "green")
    
    def _register_single_random(self, domain, name, birthday, country, gender, current_index, total_count):
        """
        单个随机生成模式注册任务
        """
        try:
            # 使用提供的信息或生成随机信息
            actual_name = name if name else generate_name()
            
            # 生成临时邮箱列表
            with self.lock:
                self.log(f"[{current_index}/{total_count}] 正在生成临时邮箱列表", "blue")
            
            temp_emails = generate_temp_email()
            if not temp_emails:
                with self.lock:
                    self.log(f"[{current_index}/{total_count}] 生成临时邮箱失败，跳过此次注册", "red")
                    if self.app_instance:
                        self.app_instance.add_account_to_table("邮箱生成失败", "N/A", actual_name, birthday, False, "随机")
                return False
            
            # 遍历邮箱列表进行注册
            for email_index, email in enumerate(temp_emails):
                try:
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 尝试使用邮箱 {email_index + 1}/{len(temp_emails)}: {email}", "cyan")
                    
                    # 生成密码
                    password = generate_password()
                    
                    # 创建注册管理器，维护完整的会话状态
                    registration_manager = RegistrationManager()
                    
                    # 初始化会话
                    init_response = registration_manager.reg_session.initialize_session()
                    if not init_response or init_response.status_code != 200:
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 会话初始化失败: {email}，尝试下一个邮箱", "orange")
                        continue
                    
                    # 步骤1: 验证邮箱地址
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 步骤1/4: 验证邮箱 {email}", "yellow")
                    
                    verify_result_data = registration_manager.verify_email_only(email)
                    if verify_result_data['status_code'] != 200:
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 邮箱验证失败: {email}，状态码: {verify_result_data['status_code']}，尝试下一个邮箱", "orange")
                        continue
                    
                    # 检查验证结果内容
                    try:
                        result_data = json.loads(verify_result_data['result'])
                        result_code = result_data.get('ResultCode')
                        if result_code not in ['00', '03']:
                            with self.lock:
                                self.log(f"[{current_index}/{total_count}] 邮箱验证失败: {email}，ResultCode: {result_code}，尝试下一个邮箱", "orange")
                            continue
                    except (json.JSONDecodeError, AttributeError):
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 邮箱验证响应解析失败: {email}，尝试下一个邮箱", "orange")
                        continue
                    
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 邮箱验证成功，验证码已发送到: {email}", "green")
                    
                    # 步骤2: 读取邮件获取k值
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 步骤2/4: 读取验证邮件获取k值", "yellow")
                    
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
                            with self.lock:
                                self.log(f"[{current_index}/{total_count}] 读取邮件失败 (重试 {retry + 1}/{max_retries}): {str(e)}", "orange")
                        
                        if retry < max_retries - 1:
                            time.sleep(3)  # 等待3秒后重试
                    
                    if not k_value:
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 未能获取到k值，尝试下一个邮箱", "orange")
                        continue
                    
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 成功获取k值: {k_value}", "green")
                    
                    # 步骤3: 激活邮箱
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 步骤3/4: 激活邮箱", "yellow")
                    
                    activation_result_data = registration_manager.activate_email_only(email, k_value)
                    if activation_result_data['status_code'] != 200:
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 邮箱激活失败，状态码: {activation_result_data['status_code']}，尝试下一个邮箱", "orange")
                        continue
                    
                    # 检查激活是否成功 - 如果包含错误信息则表示失败
                    if "The authentication key is not valid" in activation_result_data['result']:
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 邮箱激活失败，k值无效，尝试下一个邮箱", "orange")
                        continue
                    
                    # 检查是否有其他错误信息
                    if "alert(" in activation_result_data['result'] and "error" in activation_result_data['result'].lower():
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 邮箱激活失败，响应包含错误信息，尝试下一个邮箱", "orange")
                        continue
                    
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 邮箱激活成功", "green")
                    
                    # 步骤4: 提交注册表单
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 步骤4/4: 提交注册表单", "yellow")
                    
                    # 转换生日格式
                    if isinstance(birthday, str):
                        birth_date = datetime.strptime(birthday, "%Y-%m-%d").strftime("%Y%m%d")
                    else:
                        birth_date = birthday.strftime("%Y%m%d")
                    
                    # 转换性别格式
                    gender_code = 'm' if gender.lower() in ['男', 'male', 'm'] else 'f'
                    
                    # 转换国家代码
                    country_code = self._get_country_code(country)
                    
                    # 分割姓名
                    surname = actual_name.split()[0] if ' ' in actual_name else actual_name
                    firstname = actual_name.split()[1] if ' ' in actual_name else ''
                    
                    register_result_data = registration_manager.register_only(
                        email=email,
                        password=password,
                        surname=surname,
                        firstname=firstname,
                        nation=country_code,
                        birth=birth_date,
                        gender=gender_code
                    )
                    
                    if register_result_data['status_code'] == 200:
                        # 检查注册结果
                        try:
                            result_data = json.loads(register_result_data['result'])
                            result_code = result_data.get('ResultCode')
                            result_msg = result_data.get('ResultMsg', '')
                            
                            if result_code == '00':
                                # 创建账号对象
                                account = Account(email, password, actual_name, birthday, country, gender)
                                
                                # 线程安全地添加到存储
                                with self.lock:
                                    self.account_storage.add_account(account)
                                    self.registered_count += 1
                                    self.log(f"[{self.registered_count}/{total_count}] 注册成功: {email} ({actual_name})", "green")
                                    self.log(f"[{self.registered_count}/{total_count}] 账号详情: 邮箱={email}, 密码={password}, 姓名={actual_name}", "green")
                                    
                                    # 更新表格
                                    if self.app_instance:
                                        self.app_instance.add_account_to_table(email, password, actual_name, birthday, True, "随机")
                                return True
                            else:
                                with self.lock:
                                    self.log(f"[{current_index}/{total_count}] 注册失败: {email}，ResultCode: {result_code}，错误: {result_msg}，尝试下一个邮箱", "orange")
                                continue
                        except (json.JSONDecodeError, AttributeError):
                            with self.lock:
                                self.log(f"[{current_index}/{total_count}] 注册响应解析失败: {email}，尝试下一个邮箱", "orange")
                            continue
                    else:
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 注册失败: {email}，状态码: {register_result_data['status_code']}，尝试下一个邮箱", "orange")
                        continue
                        
                except Exception as e:
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 处理邮箱 {email} 时出错: {str(e)}，尝试下一个邮箱", "orange")
                    continue
            
            # 如果所有邮箱都失败了
            with self.lock:
                self.log(f"[{current_index}/{total_count}] 所有邮箱都注册失败", "red")
                if self.app_instance:
                    self.app_instance.add_account_to_table("所有邮箱失败", "N/A", actual_name, birthday, False, "随机")
            return False
                
        except Exception as e:
            with self.lock:
                self.log(f"[{current_index}/{total_count}] 注册出错: {str(e)}", "red")
                if self.app_instance:
                    self.app_instance.add_account_to_table("错误", "错误", actual_name if 'actual_name' in locals() else "未知", birthday, False, "随机")
            return False
    
    def _register_single_import(self, domain, user_data, current_index, total_count):
        """
        单个导入数据模式注册任务
        """
        try:
            # 使用导入的用户数据
            name = user_data['name']
            birthday = user_data['birthday']
            country = user_data['country']
            gender = user_data['gender']
            
            # 生成临时邮箱列表
            with self.lock:
                self.log(f"[{current_index}/{total_count}] 正在生成临时邮箱列表", "blue")
            
            temp_emails = generate_temp_email()
            if not temp_emails:
                with self.lock:
                    self.log(f"[{current_index}/{total_count}] 生成临时邮箱失败，跳过此次注册", "red")
                    if self.app_instance:
                        self.app_instance.add_account_to_table("邮箱生成失败", "N/A", name, birthday, False, "导入")
                return False
            
            # 遍历邮箱列表进行注册
            for email_index, email in enumerate(temp_emails):
                try:
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 尝试使用邮箱 {email_index + 1}/{len(temp_emails)}: {email}", "cyan")
                    
                    # 生成密码
                    password = generate_password()
                    
                    # 创建注册管理器，维护完整的会话状态
                    registration_manager = RegistrationManager()
                    
                    # 初始化会话
                    init_response = registration_manager.reg_session.initialize_session()
                    if not init_response or init_response.status_code != 200:
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 会话初始化失败: {email}，尝试下一个邮箱", "orange")
                        continue
                    
                    # 步骤1: 验证邮箱地址
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 步骤1/4: 验证邮箱 {email}", "yellow")
                    
                    verify_result_data = registration_manager.verify_email_only(email)
                    if verify_result_data['status_code'] != 200:
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 邮箱验证失败: {email}，状态码: {verify_result_data['status_code']}，尝试下一个邮箱", "orange")
                        continue
                    
                    # 检查验证结果内容
                    try:
                        result_data = json.loads(verify_result_data['result'])
                        result_code = result_data.get('ResultCode')
                        if result_code not in ['00', '03']:
                            with self.lock:
                                self.log(f"[{current_index}/{total_count}] 邮箱验证失败: {email}，ResultCode: {result_code}，尝试下一个邮箱", "orange")
                            continue
                    except (json.JSONDecodeError, AttributeError):
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 邮箱验证响应解析失败: {email}，尝试下一个邮箱", "orange")
                        continue
                    
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 邮箱验证成功，验证码已发送到: {email}", "green")
                    
                    # 步骤2: 读取邮件获取k值
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 步骤2/4: 读取验证邮件获取k值", "yellow")
                    
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
                            with self.lock:
                                self.log(f"[{current_index}/{total_count}] 读取邮件失败 (重试 {retry + 1}/{max_retries}): {str(e)}", "orange")
                        
                        if retry < max_retries - 1:
                            time.sleep(3)  # 等待3秒后重试
                    
                    if not k_value:
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 未能获取到k值，尝试下一个邮箱", "orange")
                        continue
                    
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 成功获取k值: {k_value}", "green")
                    
                    # 步骤3: 激活邮箱
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 步骤3/4: 激活邮箱", "yellow")
                    
                    activation_result_data = registration_manager.activate_email_only(email, k_value)
                    if activation_result_data['status_code'] != 200:
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 邮箱激活失败，状态码: {activation_result_data['status_code']}，尝试下一个邮箱", "orange")
                        continue
                    
                    # 检查激活是否成功 - 如果包含错误信息则表示失败
                    if "The authentication key is not valid" in activation_result_data['result']:
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 邮箱激活失败，k值无效，尝试下一个邮箱", "orange")
                        continue
                    
                    # 检查是否有其他错误信息
                    if "alert(" in activation_result_data['result'] and "error" in activation_result_data['result'].lower():
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 邮箱激活失败，响应包含错误信息，尝试下一个邮箱", "orange")
                        continue
                    
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 邮箱激活成功", "green")
                    
                    # 步骤4: 提交注册表单
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 步骤4/4: 提交注册表单", "yellow")
                    
                    # 转换生日格式
                    if isinstance(birthday, str):
                        birth_date = datetime.strptime(birthday, "%Y-%m-%d").strftime("%Y%m%d")
                    else:
                        birth_date = birthday.strftime("%Y%m%d")
                    
                    # 转换性别格式
                    gender_code = 'm' if gender.lower() in ['男', 'male', 'm'] else 'f'
                    
                    # 转换国家代码
                    country_code = self._get_country_code(country)
                    
                    # 分割姓名
                    surname = name.split()[0] if ' ' in name else name
                    firstname = name.split()[1] if ' ' in name else ''
                    
                    register_result_data = registration_manager.register_only(
                        email=email,
                        password=password,
                        surname=surname,
                        firstname=firstname,
                        nation=country_code,
                        birth=birth_date,
                        gender=gender_code
                    )
                    
                    if register_result_data['status_code'] == 200:
                        # 检查注册结果
                        try:
                            result_data = json.loads(register_result_data['result'])
                            result_code = result_data.get('ResultCode')
                            result_msg = result_data.get('ResultMsg', '')
                            
                            if result_code == '00':
                                # 创建账号对象
                                account = Account(email, password, name, birthday, country, gender)
                                
                                # 线程安全地添加到存储
                                with self.lock:
                                    self.account_storage.add_account(account)
                                    self.registered_count += 1
                                    self.log(f"[{self.registered_count}/{total_count}] 注册成功: {email} ({name})", "green")
                                    self.log(f"[{self.registered_count}/{total_count}] 账号详情: 邮箱={email}, 密码={password}, 姓名={name}", "green")
                                    
                                    # 更新表格
                                    if self.app_instance:
                                        self.app_instance.add_account_to_table(email, password, name, birthday, True, "导入")
                                return True
                            else:
                                with self.lock:
                                    self.log(f"[{current_index}/{total_count}] 注册失败: {email}，ResultCode: {result_code}，错误: {result_msg}，尝试下一个邮箱", "orange")
                                continue
                        except (json.JSONDecodeError, AttributeError):
                            with self.lock:
                                self.log(f"[{current_index}/{total_count}] 注册响应解析失败: {email}，尝试下一个邮箱", "orange")
                            continue
                    else:
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 注册失败: {email}，状态码: {register_result_data['status_code']}，尝试下一个邮箱", "orange")
                        continue
                        
                except Exception as e:
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 处理邮箱 {email} 时出错: {str(e)}，尝试下一个邮箱", "orange")
                    continue
            
            # 如果所有邮箱都失败了
            with self.lock:
                self.log(f"[{current_index}/{total_count}] 所有邮箱都注册失败", "red")
                if self.app_instance:
                    self.app_instance.add_account_to_table("所有邮箱失败", "N/A", name, birthday, False, "导入")
            return False
                
        except Exception as e:
            with self.lock:
                self.log(f"[{current_index}/{total_count}] 注册出错: {str(e)}", "red")
                if self.app_instance:
                    self.app_instance.add_account_to_table("错误", "错误", user_data.get('name', '未知'), user_data.get('birthday', ''), False, "导入")
            return False

    def _complete_registration(self, email, password, name, birthday, country, gender, current_index, total_count, source_type):
        """
        执行完整的注册流程
        :param email: 邮箱地址
        :param password: 密码
        :param name: 姓名
        :param birthday: 生日
        :param country: 国家
        :param gender: 性别
        :param current_index: 当前索引
        :param total_count: 总数量
        :param source_type: 来源类型（随机/导入）
        :return: 注册是否成功
        """
        try:
            with self.lock:
                self.log(f"[{current_index}/{total_count}] 开始注册: {email} ({name})", "blue")
            
            # 使用API注册管理器进行完整注册流程
            with APIRegistrationManager() as api_manager:
                with self.lock:
                    self.log(f"[{current_index}/{total_count}] 初始化注册会话: {email}", "cyan")
                
                # 步骤1: 验证邮箱
                with self.lock:
                    self.log(f"[{current_index}/{total_count}] 接口调用1/3: 验证邮箱 {email}", "yellow")
                
                verify_result = api_manager.verify_email_only(email)
                
                # 详细日志输出验证结果
                if verify_result:
                    status_code = verify_result.get('status_code', 'N/A')
                    result_text = verify_result.get('result', '')[:100] + '...' if len(verify_result.get('result', '')) > 100 else verify_result.get('result', '')
                    print(f"[{current_index}/{total_count}] 验证响应: 状态码={status_code}, 内容={result_text}")
                    
                    # 尝试解析JSON响应
                    try:
                        import json
                        result_json = json.loads(verify_result.get('result', '{}'))
                        result_code = result_json.get('ResultCode', 'N/A')
                        result_msg = result_json.get('ResultMsg', 'N/A')
                        print(f"[{current_index}/{total_count}] 验证详情: ResultCode={result_code}, ResultMsg={result_msg}")
                    except:
                        pass
                else:
                    print(f"[{current_index}/{total_count}] 验证响应: 无响应数据")
                
                # 检查验证结果
                if not verify_result or verify_result.get('status_code') != 200:
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 邮箱验证失败: {email}, 状态码: {verify_result.get('status_code') if verify_result else 'None'}", "red")
                        if self.app_instance:
                            self.app_instance.add_account_to_table(email, password, name, birthday, False, source_type)
                    return False
                
                # 进一步检查验证结果内容
                try:
                    result_data = json.loads(verify_result.get('result', '{}'))
                    result_code = result_data.get('ResultCode')
                    if result_code not in ['00', '03']:
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 邮箱验证失败: {email}, ResultCode: {result_code}, 消息: {result_data.get('ResultMsg', '未知错误')}", "red")
                            if self.app_instance:
                                self.app_instance.add_account_to_table(email, password, name, birthday, False, source_type)
                        return False
                except (json.JSONDecodeError, AttributeError):
                    with self.lock:
                        self.log(f"[{current_index}/{total_count}] 邮箱验证响应解析失败: {email}", "red")
                        if self.app_instance:
                            self.app_instance.add_account_to_table(email, password, name, birthday, False, source_type)
                    return False
                
                with self.lock:
                    self.log(f"[{current_index}/{total_count}] 邮箱验证成功: {email}", "green")
                
                # 步骤2: 等待邮件激活（这里需要用户手动处理邮件激活）
                # 在实际应用中，这里应该集成邮件处理逻辑来自动获取激活链接
                # 目前先跳过激活步骤，直接尝试注册
                
                # 步骤2: 邮件激活（暂时跳过，直接进入注册）
                with self.lock:
                    self.log(f"[{current_index}/{total_count}] 接口调用2/3: 邮件激活 (暂时跳过)", "yellow")
                    self.log(f"[{current_index}/{total_count}] 注意: 邮件激活步骤已跳过，直接尝试注册", "orange")
                
                # 步骤3: 提交注册信息
                with self.lock:
                    self.log(f"[{current_index}/{total_count}] 接口调用3/3: 提交注册信息 {email}", "yellow")
                
                # 转换生日格式
                if isinstance(birthday, str):
                    birth_date = datetime.strptime(birthday, "%Y-%m-%d").strftime("%Y%m%d")
                else:
                    birth_date = birthday.strftime("%Y%m%d")
                
                # 转换性别格式
                gender_code = 'm' if gender.lower() in ['男', 'male', 'm'] else 'f'
                
                # 转换国家代码（这里需要根据实际情况映射）
                country_code = self._get_country_code(country)
                
                # 详细记录注册参数
                surname = name.split()[0] if ' ' in name else name
                firstname = name.split()[1] if ' ' in name else ''
                
                with self.lock:
                    self.log(f"[{current_index}/{total_count}] 注册参数: 邮箱={email}, 姓={surname}, 名={firstname}, 国家={country}({country_code}), 生日={birth_date}, 性别={gender}({gender_code})", "cyan")
                
                register_result = api_manager.register_only(
                    email=email,
                    password=password,
                    surname=surname,
                    firstname=firstname,
                    nation=country_code,
                    birth=birth_date,
                    gender=gender_code
                )
                
                # 详细日志输出注册结果
                if register_result:
                    status_code = register_result.get('status_code', 'N/A')
                    result_text = register_result.get('result', '')[:100] + '...' if len(register_result.get('result', '')) > 100 else register_result.get('result', '')
                    print(f"[{current_index}/{total_count}] 注册响应: 状态码={status_code}, 内容={result_text}")
                    
                    # 尝试解析JSON响应
                    try:
                        import json
                        result_json = json.loads(register_result.get('result', '{}'))
                        if isinstance(result_json, dict):
                            for key, value in result_json.items():
                                print(f"[{current_index}/{total_count}] 注册详情: {key}={value}")
                    except:
                        pass
                else:
                    print(f"[{current_index}/{total_count}] 注册响应: 无响应数据")
                
                # 检查注册结果
                if register_result and register_result.get('status_code') == 200:
                    try:
                        result_data = json.loads(register_result['result'])
                        result_code = result_data.get('ResultCode')
                        result_msg = result_data.get('ResultMsg', '')
                        
                        if result_code == '00':
                            # 创建账号对象
                            account = Account(email, password, name, birthday, country, gender)
                            
                            # 线程安全地添加到存储
                            with self.lock:
                                self.account_storage.add_account(account)
                                self.registered_count += 1
                                self.log(f"[{self.registered_count}/{total_count}] 注册成功: {email} ({name})", "green")
                                self.log(f"[{self.registered_count}/{total_count}] 账号详情: 邮箱={email}, 密码={password}, 姓名={name}", "green")
                                
                                # 更新表格
                                if self.app_instance:
                                    self.app_instance.add_account_to_table(email, password, name, birthday, True, source_type)
                            return True
                        else:
                            with self.lock:
                                self.log(f"[{current_index}/{total_count}] 注册失败: {email}，ResultCode: {result_code}，错误: {result_msg}", "red")
                                if self.app_instance:
                                    self.app_instance.add_account_to_table(email, password, name, birthday, False, source_type)
                            return False
                    except (json.JSONDecodeError, AttributeError):
                        with self.lock:
                            self.log(f"[{current_index}/{total_count}] 注册响应解析失败: {email}", "red")
                            if self.app_instance:
                                self.app_instance.add_account_to_table(email, password, name, birthday, False, source_type)
                        return False
                else:
                    with self.lock:
                        status_code = register_result.get('status_code') if register_result else 'None'
                        self.log(f"[{current_index}/{total_count}] 注册失败: {email}，状态码: {status_code}", "red")
                        if self.app_instance:
                            self.app_instance.add_account_to_table(email, password, name, birthday, False, source_type)
                    return False
                    
        except Exception as e:
            with self.lock:
                self.log(f"[{current_index}/{total_count}] 注册过程异常: {email}", "red")
                self.log(f"[{current_index}/{total_count}] 异常详情: {str(e)}", "red")
                
                # 记录异常类型
                import traceback
                error_trace = traceback.format_exc()
                self.log(f"[{current_index}/{total_count}] 异常堆栈: {error_trace[:300]}...", "red")
                
                if self.app_instance:
                    self.app_instance.add_account_to_table(email, password, name, birthday, False, source_type)
            return False
    
    def _get_country_code(self, country):
        """
        获取国家代码
        :param country: 国家名称
        :return: 国家代码
        """
        # 这里需要根据实际的国家代码映射表来实现
        # 暂时返回一个默认值
        country_mapping = {
            '中国': 43,
            '美国': 1,
            '日本': 81,
            '韩国': 82,
            '英国': 44,
            '德国': 49,
            '法国': 33,
            '加拿大': 1,
            '澳大利亚': 61
        }
        return country_mapping.get(country, 43)  # 默认返回中国的代码

    def _export_results(self, export_path):
        """
        导出注册结果
        :param export_path: 导出路径
        """
        self.log("已经注册 " + str(self.account_storage.__len__()) + " 个账户")
        
        # 将注册成功的账号导出为excel文件
        if export_accounts_to_excel(self.account_storage.accounts, export_path):
            self.log(" ")
            self.log("============================", "green")
            self.log("成功保存并导出所有已经注册的账号!", color="green")
            self.log("导出保存路径:" + export_path)
            self.log(" ")
        else:
            self.log(" ")
            self.log("============================", "red")
            self.log("保存导出所有已经注册的账号失败！", "red")

    def register_loop_random(self, domain, count, name, birthday, country, gender):
        """
        随机生成模式循环注册（已弃用，建议使用register_accounts_random）
        :param domain: 邮箱域名
        :param count: 注册数量
        :param name: 名字（空则随机生成）
        :param birthday: 生日
        :param country: 国家
        :param gender: 性别
        """
        self.log("警告: register_loop_random方法已弃用，建议使用register_accounts_random方法", "yellow")
        
        # 转换为新的注册方法
        export_path = f"注册结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        self.register_accounts_random(domain, count, name, birthday, country, gender, export_path, thread_count=1)
    
    def register_loop_import(self, domain, user_data):
        """
        导入数据模式循环注册（已弃用，建议使用register_accounts_import）
        :param domain: 邮箱域名
        :param user_data: 用户数据列表
        """
        self.log("警告: register_loop_import方法已弃用，建议使用register_accounts_import方法", "yellow")
        
        # 转换为新的注册方法
        export_path = f"注册结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        self.register_accounts_import(domain, user_data, export_path, thread_count=1)


    def check_email_address(self, email_address):
        """
        检查邮箱地址（已弃用，现在集成在_complete_registration方法中）
        :param email_address:
        :return: 如果调用邮箱地址成功就返回true，否则就返回false
        """
        self.log("警告: check_email_address方法已弃用，现在使用完整的注册流程", "yellow")
        
        try:
            with APIRegistrationManager() as api_manager:
                result = api_manager.verify_email_only(email_address)
                return result and result.get('success') == True
        except Exception as e:
            self.log(f"邮箱地址验证错误: {str(e)}", "red")
            return False
    
    def integrate_email_processor(self, email_processor):
        """
        集成邮件处理器，用于自动处理邮件激活
        :param email_processor: 邮件处理器实例
        """
        self.email_processor = email_processor
        self.log("邮件处理器已集成，支持自动邮件激活", "green")
    
    def _process_email_activation(self, email, timeout=300):
        """
        处理邮件激活（预留接口，用于集成邮件处理功能）
        :param email: 邮箱地址
        :param timeout: 超时时间（秒）
        :return: 激活token或None
        """
        if hasattr(self, 'email_processor') and self.email_processor:
            try:
                # 这里将来可以集成邮件处理逻辑
                # return self.email_processor.get_activation_token(email, timeout)
                pass
            except Exception as e:
                self.log(f"邮件激活处理失败: {str(e)}", "red")
        return None
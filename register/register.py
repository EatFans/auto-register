from account import Account
from api.register_api import *
from util.generate_util import *
from datetime import datetime
from account_storage import AccountStorage
from util.excel_util import *
import json
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed

class RegisterManager:
    def __init__(self, log_callback=None):
        """
        初始化注册管理器
        
        :param log_callback: 日志回调函数，接收消息和颜色两个参数
        """
        self.log_callback = log_callback
        self.email_handler = None
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
        self.log(f"开始使用 {thread_count} 个线程进行注册...")
        
        # 创建线程锁，保护共享资源
        self.lock = threading.Lock()
        self.registered_count = 0
        
        # 使用线程池执行注册任务
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            # 提交注册任务
            futures = []
            for i in range(count):
                future = executor.submit(self._register_single_random, domain, name, birthday, country, gender, i+1, count)
                futures.append(future)
            
            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.log(f"注册任务执行出错: {str(e)}", "red")
    
    def _register_with_threads_import(self, domain, user_data, thread_count):
        """
        使用多线程进行导入数据模式注册
        """
        self.log(f"开始使用 {thread_count} 个线程进行注册...")
        
        # 创建线程锁，保护共享资源
        self.lock = threading.Lock()
        self.registered_count = 0
        
        # 使用线程池执行注册任务
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            # 提交注册任务
            futures = []
            for i, user in enumerate(user_data):
                future = executor.submit(self._register_single_import, domain, user, i+1, len(user_data))
                futures.append(future)
            
            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.log(f"注册任务执行出错: {str(e)}", "red")
    
    def _register_single_random(self, domain, name, birthday, country, gender, current_index, total_count):
        """
        单个随机生成模式注册任务
        """
        try:
            # 生成邮箱和密码
            email = generate_email(domain)
            password = generate_password()
            
            # 使用提供的信息或生成随机信息
            actual_name = name if name else generate_name()
            
            # 验证邮箱
            if self.check_email_address(email):
                # 创建账号对象
                account = Account(email, password, actual_name, birthday, country, gender)
                
                # 线程安全地添加到存储
                with self.lock:
                    self.account_storage.add_account(account)
                    self.registered_count += 1
                    self.log(f"[{self.registered_count}/{total_count}] 注册成功: {email}", "green")
            else:
                with self.lock:
                    self.log(f"[{current_index}/{total_count}] 邮箱验证失败: {email}", "red")
        except Exception as e:
            with self.lock:
                self.log(f"[{current_index}/{total_count}] 注册出错: {str(e)}", "red")
    
    def _register_single_import(self, domain, user_data, current_index, total_count):
        """
        单个导入数据模式注册任务
        """
        try:
            # 生成邮箱和密码
            email = generate_email(domain)
            password = generate_password()
            
            # 使用导入的用户数据
            name = user_data['name']
            birthday = user_data['birthday']
            country = user_data['country']
            gender = user_data['gender']
            
            # 验证邮箱
            if self.check_email_address(email):
                # 创建账号对象
                account = Account(email, password, name, birthday, country, gender)
                
                # 线程安全地添加到存储
                with self.lock:
                    self.account_storage.add_account(account)
                    self.registered_count += 1
                    self.log(f"[{self.registered_count}/{total_count}] 注册成功: {email} ({name})", "green")
            else:
                with self.lock:
                    self.log(f"[{current_index}/{total_count}] 邮箱验证失败: {email} ({name})", "red")
        except Exception as e:
            with self.lock:
                self.log(f"[{current_index}/{total_count}] 注册出错: {str(e)}", "red")
    
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
        随机生成模式循环注册
        :param domain: 邮箱域名
        :param count: 注册数量
        :param name: 名字（空则随机生成）
        :param birthday: 生日
        :param country: 国家
        :param gender: 性别
        """
        i = 0
        while i < count:
            self.log(" ")
            self.log(f"开始注册第 {i+1} 个账号...", "blue")
            flag = False
            
            # 随机生成邮箱别名
            email_address = generate_email(domain, 10)
            self.log("已生成邮箱地址: " + email_address, "green")
            
            # 验证邮箱地址
            if self.check_email_address(email_address):
                self.log("邮箱地址验证成功！", "green")
                flag = True
            # TODO: 通过邮箱获取邮件中的token来激活邮箱

            # 随机生成密码
            password = generate_password()
            self.log("已生成密码: " + password, "green")

            # 使用指定名字或随机生成
            current_name = name if name else generate_name()
            self.log("使用名字: " + current_name, "green")

            account = Account(
                email_address,
                password,
                current_name,
                datetime.strptime(birthday, "%Y-%m-%d").date(),
                country,
                gender
            )
            
            # TODO: 发送提交注册请求
            if flag:
                self.account_storage.add(account)
                self.log("账号注册成功！", "green")
            else:
                self.log("账号注册失败！", "red")
            i += 1
    
    def register_loop_import(self, domain, user_data):
        """
        导入数据模式循环注册
        :param domain: 邮箱域名
        :param user_data: 用户数据列表
        """
        for i, user_info in enumerate(user_data):
            self.log(" ")
            self.log(f"开始注册第 {i+1} 个账号...", "blue")
            flag = False
            
            # 随机生成邮箱别名
            email_address = generate_email(domain, 10)
            self.log("已生成邮箱地址: " + email_address, "green")
            
            # 验证邮箱地址
            if self.check_email_address(email_address):
                self.log("邮箱地址验证成功！", "green")
                flag = True
            # TODO: 通过邮箱获取邮件中的token来激活邮箱

            # 随机生成密码
            password = generate_password()
            self.log("已生成密码: " + password, "green")

            # 使用导入的用户信息
            name = user_info['name']
            birthday = user_info['birthday']
            country = user_info['country']
            gender = user_info['gender']
            
            self.log(f"使用导入信息 - 姓名: {name}, 生日: {birthday}, 国家: {country}, 性别: {gender}", "green")

            account = Account(
                email_address,
                password,
                name,
                datetime.strptime(birthday, "%Y-%m-%d").date(),
                country,
                gender
            )
            
            # TODO: 发送提交注册请求
            if flag:
                self.account_storage.add(account)
                self.log("账号注册成功！", "green")
            else:
                self.log("账号注册失败！", "red")


    def check_email_address(self, email_address):
        """
        检查邮箱地址
        :param email_address:
        :return: 如果调用邮箱地址成功就返回true，否则就返回false
        """
        response = verify_email_address(email_address)
        if not response or response.status_code != 200:
            self.log("邮箱地址验证错误！","red")
            return False
        # 检查响应体中resultCode
        try:
            data = response.json()
        except json.JSONDecodeError:
            self.log("接口返回数据不是有效JSON格式！","red")
            return False
        result_code = data.get("ResultCode")
        if result_code != "00":
            self.log("邮箱地址验证错误！","red")
            return False
        print(response.text) # 测试用
        return True
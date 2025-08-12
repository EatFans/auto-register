# 基础注册流程抽象类
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from account_storage import AccountStorage
from entity.account import Account
from util.excel_util import export_accounts_to_excel
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class BaseRegisterManager(ABC):
    """
    基础注册管理器抽象类
    所有网站的注册管理器都应该继承此类
    """
    
    def __init__(self, log_callback=None, app_instance=None):
        """
        初始化基础注册管理器
        
        :param log_callback: 日志回调函数，接收消息和颜色两个参数
        :param app_instance: Application实例，用于更新表格
        """
        self.log_callback = log_callback
        self.app_instance = app_instance
        self.account_storage = AccountStorage()
        self.lock = threading.Lock()
        self.registered_count = 0
    
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
    
    @abstractmethod
    def get_website_name(self) -> str:
        """
        获取网站名称
        :return: 网站名称
        """
        pass
    
    @abstractmethod
    def validate_config(self, **kwargs) -> bool:
        """
        验证配置是否有效
        :param kwargs: 配置参数
        :return: 配置是否有效
        """
        pass
    
    @abstractmethod
    def _register_single_account(self, email: str, password: str, user_data: Dict, **kwargs) -> bool:
        """
        注册单个账号的具体实现
        :param email: 邮箱地址
        :param password: 密码
        :param user_data: 用户数据字典
        :param kwargs: 其他参数
        :return: 注册是否成功
        """
        pass
    
    @abstractmethod
    def _verify_email(self, email: str, **kwargs) -> bool:
        """
        验证邮箱的具体实现
        :param email: 邮箱地址
        :param kwargs: 其他参数
        :return: 验证是否成功
        """
        pass
    
    def register_accounts_random(self, domain, count, name, birthday, country, gender, export_path, thread_count=5, **kwargs):
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
        :param kwargs: 其他参数
        """
        # 清空之前的账号存储
        self.account_storage.clear()
        
        # 验证配置
        if not self.validate_config(domain=domain, **kwargs):
            self.log(f"配置验证失败，无法开始注册", "red")
            return
        
        # 多线程注册
        self._register_with_threads_random(domain, count, name, birthday, country, gender, thread_count, **kwargs)
        
        # 导出结果
        self._export_results(export_path)
    
    def register_accounts_import(self, domain, user_data, export_path, thread_count=5, **kwargs):
        """
        导入数据模式注册账号
        :param domain: 邮箱域名
        :param user_data: 导入的用户数据列表
        :param export_path: 导出路径
        :param thread_count: 线程数
        :param kwargs: 其他参数
        """
        # 清空之前的账号存储
        self.account_storage.clear()
        
        # 验证配置
        if not self.validate_config(domain=domain, **kwargs):
            self.log(f"配置验证失败，无法开始注册", "red")
            return
        
        # 多线程注册
        self._register_with_threads_import(domain, user_data, thread_count, **kwargs)
        
        # 导出结果
        self._export_results(export_path)
    
    def _register_with_threads_random(self, domain, count, name, birthday, country, gender, thread_count, **kwargs):
        """
        使用多线程进行随机生成模式注册
        """
        self.log(f"开始使用 {thread_count} 个线程进行{self.get_website_name()}随机注册，目标数量: {count}", "blue")
        self.log(f"注册参数: 域名={domain}, 姓名={name}, 生日={birthday}, 国家={country}, 性别={gender}", "blue")
        
        # 重置计数器
        self.registered_count = 0
        
        # 使用线程池执行注册任务
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            # 提交注册任务
            futures = []
            self.log(f"正在提交 {count} 个注册任务到线程池...", "cyan")
            
            for i in range(count):
                future = executor.submit(self._register_single_random_wrapper, domain, name, birthday, country, gender, i+1, count, **kwargs)
                futures.append(future)
            
            self.log(f"所有任务已提交，等待执行完成...", "cyan")
            
            # 等待所有任务完成
            completed_tasks = 0
            for future in as_completed(futures):
                try:
                    result = future.result()
                    completed_tasks += 1
                    self.log(f"任务完成进度: {completed_tasks}/{count}", "cyan")
                except Exception as e:
                    self.log(f"任务执行异常: {str(e)}", "red")
                    completed_tasks += 1
            
            self.log(f"所有注册任务已完成！成功注册: {self.registered_count}/{count}", "green")
    
    def _register_with_threads_import(self, domain, user_data, thread_count, **kwargs):
        """
        使用多线程进行导入数据模式注册
        """
        count = len(user_data)
        self.log(f"开始使用 {thread_count} 个线程进行{self.get_website_name()}导入注册，目标数量: {count}", "blue")
        
        # 重置计数器
        self.registered_count = 0
        
        # 使用线程池执行注册任务
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            # 提交注册任务
            futures = []
            self.log(f"正在提交 {count} 个注册任务到线程池...", "cyan")
            
            for i, data in enumerate(user_data):
                future = executor.submit(self._register_single_import_wrapper, domain, data, i+1, count, **kwargs)
                futures.append(future)
            
            self.log(f"所有任务已提交，等待执行完成...", "cyan")
            
            # 等待所有任务完成
            completed_tasks = 0
            for future in as_completed(futures):
                try:
                    result = future.result()
                    completed_tasks += 1
                    self.log(f"任务完成进度: {completed_tasks}/{count}", "cyan")
                except Exception as e:
                    self.log(f"任务执行异常: {str(e)}", "red")
                    completed_tasks += 1
            
            self.log(f"所有注册任务已完成！成功注册: {self.registered_count}/{count}", "green")
    
    def _register_single_random_wrapper(self, domain, name, birthday, country, gender, current_index, total_count, **kwargs):
        """
        随机注册单个账号的包装方法
        """
        # 子类需要实现具体的注册逻辑
        return self._register_single_random(domain, name, birthday, country, gender, current_index, total_count, **kwargs)
    
    def _register_single_import_wrapper(self, domain, user_data, current_index, total_count, **kwargs):
        """
        导入注册单个账号的包装方法
        """
        # 子类需要实现具体的注册逻辑
        return self._register_single_import(domain, user_data, current_index, total_count, **kwargs)
    
    @abstractmethod
    def _register_single_random(self, domain, name, birthday, country, gender, current_index, total_count, **kwargs):
        """
        随机注册单个账号的具体实现
        子类必须实现此方法
        """
        pass
    
    @abstractmethod
    def _register_single_import(self, domain, user_data, current_index, total_count, **kwargs):
        """
        导入注册单个账号的具体实现
        子类必须实现此方法
        """
        pass
    
    def _export_results(self, export_path):
        """
        导出注册结果
        :param export_path: 导出路径
        """
        if not export_path:
            self.log("未指定导出路径，跳过导出", "yellow")
            return
        
        accounts = self.account_storage.get_all()
        if not accounts:
            self.log("没有账号数据可导出", "yellow")
            return
        
        try:
            success = export_accounts_to_excel(accounts, export_path)
            if success:
                self.log(f"账号数据已成功导出到: {export_path}", "green")
            else:
                self.log(f"导出失败: {export_path}", "red")
        except Exception as e:
            self.log(f"导出异常: {str(e)}", "red")
    
    def add_account_to_storage(self, account: Account):
        """
        添加账号到存储
        :param account: 账号对象
        """
        self.account_storage.add(account)
        
        # 更新UI表格
        if self.app_instance:
            self.app_instance.add_account_to_table(
                account.email, 
                account.password, 
                account.name, 
                account.birthday, 
                "已完成", 
                self.get_website_name()
            )
    
    def update_registered_count(self):
        """
        更新注册成功计数
        """
        with self.lock:
            self.registered_count += 1
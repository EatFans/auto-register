from account import Account
from api.register_api import *
from util.generate_util import *
from datetime import datetime
from account_storage import AccountStorage
from util.excel_util import *
import json

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
    
    def register_accounts_random(self, domain, count, name, birthday, country, gender, export_path):
        """
        随机生成模式注册账号
        :param domain: 邮箱域名
        :param count: 注册数量
        :param name: 名字（空则随机生成）
        :param birthday: 生日
        :param country: 国家
        :param gender: 性别
        :param export_path: 导出路径
        """
        # 清空之前的账号存储
        self.account_storage.clear()
        
        # 循环注册
        self.register_loop_random(domain, count, name, birthday, country, gender)
        
        # 导出结果
        self._export_results(export_path)
    
    def register_accounts_import(self, domain, user_data, export_path):
        """
        导入数据模式注册账号
        :param domain: 邮箱域名
        :param user_data: 导入的用户数据列表
        :param export_path: 导出路径
        """
        # 清空之前的账号存储
        self.account_storage.clear()
        
        # 循环注册
        self.register_loop_import(domain, user_data)
        
        # 导出结果
        self._export_results(export_path)
    
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
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
    
    def register_accounts(self, domain,count,name,birthday,country,gender,export_path):
        """
        注册账号

        """
        # 循环注册
        self.register_loop(domain,count,name,birthday,country,gender)
        #
        self.log("已经注册 "+str(self.account_storage.__len__()) + " 个账户")


        # 将注册成功的账号导出为excel文件
        if export_accounts_to_excel(self.account_storage.accounts, export_path):
            self.log(" ")
            self.log("============================","green")
            self.log("成功保存并导出所有已经注册的账号!", color="green")
            self.log("导出保存路径:" + export_path)
            self.log(" ")

        else:
            self.log(" ")
            self.log("============================","red")
            self.log("保存导出所有已经注册的账号失败！","red")

    def register_loop(self,domain,count,name,birthday,country,gender):
        """
        循环注册并添加已经注册好的账号
        :param domain:
        :param gender:
        :param name:
        :param birthday:
        :param country:
        :param count: 需要注册的数量
        """
        i = 0
        while i < count:
            self.log(" ")
            flag = False
            # 随机生成邮箱别名
            email_address = generate_email(domain, 10)
            self.log("已生成邮箱地址: " + email_address, "green")
            # 验证邮箱地址
            if self.check_email_address(email_address):
                self.log("邮箱地址验证成功！","green")
                flag = True
            # TODO: 通过邮箱获取邮件中的token来激活邮箱

            # 随机生成密码
            password = generate_password()

            current_name = name if name else generate_name()

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
                self.log("账号注册成功！","green")
            else:
                self.log("账号注册失败！","red")
            i += 1


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
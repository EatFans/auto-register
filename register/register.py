from account import Account
from api.register_api import *
from util.generate_util import *
from datetime import date
from account_storage import AccountStorage
from util.excel_util import *

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
    
    def register_accounts(self, count,  random_user, random_pwd,):
        """
        注册账号

        """
        # 循环注册
        self.register_loop(count)
        #
        self.log("已经注册 "+str(self.account_storage.__len__()) + " 个账户")

        # 将注册成功的账号导出为excel文件
        if export_accounts_to_excel(self.account_storage.accounts,"测试.xlsx"):
            self.log(" ")
            self.log("============================","green")
            self.log("成功保存并导出所有已经注册的账号!", color="green")
            self.log(" ")
        else:
            self.log(" ")
            self.log("============================","red")
            self.log("保存导出所有已经注册的账号失败！","red")

    def register_loop(self,count):
        """
        循环注册并添加已经注册好的账号
        :param count: 需要注册的数量
        """
        i = 0
        while i < count:
            # 随机生成邮箱别名
            email_address = generate_email("@test.com", 10)
            # TODO: 验证邮箱地址
            # TODO: 发送邮箱激活码请求
            # TODO: 通过邮箱获取邮件
            # 随机生成密码
            password = generate_password()
            name = '小红'
            birthday = date(2000,1,1)
            country = 'China'
            gender = 'f'

            account = Account(
                email_address,
                password,
                name,
                birthday,
                country,
                gender
            )
            # TODO: 发送提交注册请求

            self.account_storage.add(account)
            self.log(email_address, "green")
            i += 1


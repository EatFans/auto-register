from account import Account
from api.register_api import *
from util.generate_util import *
from datetime import date
from account_storage import AccountStorage
from typing import List


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
        self.log("已经生成了 "+str(self.account_storage.__len__()) + " 个账户")

        for acc in self.account_storage.accounts:
            self.log(acc.email)
        # TODO: 随机生成邮箱别名
        # TODO: 验证邮箱地址
        # TODO: 发送邮箱激活码请求
        # TODO: 通过邮箱获取邮件
        # res = verify_email_address("2180654922@qq.com")
        # k = '7587d80f-4ea0-4f75-a9ab-89ae1f209adf'
        # res = activationEmail("eatfan0921@163.com",k)
        # self.log("响应状态："+ str(res.status_code),"green")
        # self.log("响应体内容:" + res.text,"red")
        # print(res.text)

    def register_loop(self,count):
        i = 0
        while i < count:
            email_address = generate_email("@test.com", 10)
            password = '123456'
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
            self.account_storage.add(account)
            self.log(email_address, "red")
            i += 1


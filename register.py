from register_api import *

class RegisterManager:
    def __init__(self, log_callback=None):
        """
        初始化注册管理器
        
        :param log_callback: 日志回调函数，接收消息和颜色两个参数
        """
        self.log_callback = log_callback

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
        a = 0
        while a < count:
            a += 1
            self.log(" ")
            self.register_loop()
            self.log("已经注册 " + str(a) + " 个账号","black")



    def register_loop(self):
        verifyEmailAddress("test")
        self.log("验证邮箱成功", "green")
        activationEmail("test", "test-key")
        self.log("激活邮箱成功", "green")
        register("test")
        self.log("用户注册成功", "green")
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
        res = verifyEmailAddress("2180654922@qq.com")
        k = '7587d80f-4ea0-4f75-a9ab-89ae1f209adf'
        # res = activationEmail("eatfan0921@163.com",k)
        self.log("响应状态："+ str(res.status_code),"green")
        self.log("响应体内容:" + res.text,"red")
        print(res.text)

    def register_loop(self):
        verifyEmailAddress("test")

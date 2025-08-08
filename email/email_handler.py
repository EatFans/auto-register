# 邮件处理

class EmailHandler:
    def __init__(self, imap_host, email_user,email_pass):
        print("初始化邮件处理...")
        self.imap_host = imap_host
        self.email_user = email_user
        self.email_pass = email_pass
        print("初始化邮件处理成功")

    def connect(self):
        print("链接邮箱中")

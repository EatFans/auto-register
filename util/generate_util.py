# 生成工具

import random
import string
import time

used_email_address = set() # 已经使用过的邮箱地址合集


def generate_email(domain='@163.com',length=10):
    """
    随机生成邮箱
    :param domain: 邮箱域名例如@163.com 
    :param length: 别名长度
    :return: 返回生成好的完整邮箱地址
    """
    while True:
        timestamp = int(time.time() * 1000) # 毫秒时间戳
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))  #随机挑选字母和数字
        email_address = f"{random_part}{timestamp % 10000}@{domain.lstrip('@')}"
        if email_address not in used_email_address:
            used_email_address.add(email_address)
            return email_address

# TODO
def generate_password():
    """
    随机生成密码
    :return: 返回生成好的密码
    """
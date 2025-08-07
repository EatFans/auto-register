# 生成工具

import random
import string
import time
from faker import Faker

fake = Faker("en_US")

used_email_address = set() # 已经使用过的邮箱地址合集



def generate_email(domain='163.com',length=10):
    """
    随机生成邮箱
    :param domain: 邮箱域名例如@163.com 
    :param length: 别名长度
    :return: 返回生成好的完整邮箱地址
    """
    while True:
        timestamp = int(time.time() * 1000) # 毫秒时间戳
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))  #随机挑选字母和数字
        email_address = f"{random_part}{timestamp % 10000}@{domain}"
        if email_address not in used_email_address:
            used_email_address.add(email_address)
            return email_address

def generate_password(length=12) -> str:
    """
    随机生成密码
    :param length: 密码长度，默认为12
    :return: 返回生成好的密码字符串
    """
    # 定义字符集
    upper = string.ascii_uppercase
    lower = string.ascii_lowercase
    digits = string.digits
    symbols = "!@#$%^&*()-_"

    # 确保密码至少包含一种每类字符
    base = [
        random.choice(upper),
        random.choice(lower),
        random.choice(digits),
        random.choice(symbols)
    ]

    # 补足剩余长度的随机字符串
    all_chars = upper + lower + digits + symbols
    base += random.choices(all_chars,k=length-len(base))
    # 打乱顺序
    random.shuffle(base)
    return ''.join(base)


def generate_name() -> str:
    """
    随机生成简单英文名字
    :return: 返回生成好的英文名
    """
    return fake.name()

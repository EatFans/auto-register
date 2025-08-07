# 字符串处理工具
import datetime

def validate_birthday(birthday_str):
    """
    检查生日时间是否合法
    :param birthday_str: 生日时间字符串
    :return:  如果合法就返回true，否则就返回false
    """
    try:
        datetime.datetime.strptime(birthday_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False
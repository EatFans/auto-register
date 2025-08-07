# Excel表格处理工具
from openpyxl.workbook import Workbook
import os
from account import Account
from typing import List

def export_accounts_to_excel(accounts: List[Account], filepath: str):
    """
    导出账号数据excel表格
    :param accounts: 账号数据
    :param filepath: 导出文件路径
    :return: 如果导出保存成功就返回true，否则就返回false
    """
    try:
        # 创建 Excel 工作簿和工作表
        wb = Workbook()
        ws = wb.active
        ws.title = "Accounts"
        # 写入表头
        headers = ['邮箱','密码','名字','生日','国家区域','性别']
        ws.append(headers)
        # 写入每一行数据
        for account in accounts:
            ws.append([
                account.email,
                account.password,
                account.name,
                account.birthday.strftime('%Y-%m-%d'),
                account.country,
                account.gender
            ])
        # 保存文件到指定路径
        wb.save(filepath)
        return True
    except Exception as e:
        print(e)
        return False

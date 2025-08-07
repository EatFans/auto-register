# 账号状态存储
from typing import List
from account import Account

class AccountStorage:
    def __init__(self):
        self.accounts: List[Account] = [] # 初始化账号缓存列表

    # 添加账号
    def add(self, account: Account):
        self.accounts.append(account)

    # 获取完整列表
    def get_all(self) -> List[Account]:
        return self.accounts

    # 清理
    def clear(self):
        self.accounts.clear()

    # 长度
    def __len__(self):
        return len(self.accounts)
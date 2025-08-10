# 账号状态存储
from typing import List
from entity.account import Account
import threading

class AccountStorage:
    def __init__(self):
        self.accounts: List[Account] = [] # 初始化账号缓存列表
        self.lock = threading.Lock()  # 线程锁

    # 添加账号
    def add(self, account: Account):
        with self.lock:
            self.accounts.append(account)
    
    # 添加账号（别名方法，保持兼容性）
    def add_account(self, account: Account):
        self.add(account)

    # 获取完整列表
    def get_all(self) -> List[Account]:
        with self.lock:
            return self.accounts.copy()  # 返回副本以避免并发修改

    # 清理
    def clear(self):
        with self.lock:
            self.accounts.clear()

    # 长度
    def __len__(self):
        with self.lock:
            return len(self.accounts)
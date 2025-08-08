import datetime
from dataclasses import dataclass
from typing import Union

@dataclass
class Account:
    email: str
    password: str
    name: str
    birthday: Union[str, datetime.date]  # 支持字符串和日期对象
    country: str
    gender: str

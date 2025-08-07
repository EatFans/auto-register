import datetime
from dataclasses import dataclass

@dataclass
class Account:
    email: str
    password: str
    name: str
    birthday: datetime.date
    country: str
    gender: str

# 导入工具
import pandas as pd
from typing import List, Dict
import os
from datetime import datetime

class UserDataImporter:
    def __init__(self):
        self.user_data = []
    
    def import_from_excel(self, file_path: str) -> bool:
        """
        从Excel文件导入用户数据
        :param file_path: Excel文件路径
        :return: 导入是否成功
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 检查必需的列
            required_columns = ['姓名', '生日', '国家', '性别']
            # 检查是否有Melon注册需要的额外字段
            melon_columns = ['邮箱', '邮箱密钥']
            has_melon_fields = all(col in df.columns for col in melon_columns)
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Excel文件缺少必需的列: {', '.join(missing_columns)}")
            
            # 清空之前的数据
            self.user_data.clear()
            
            # 处理每一行数据
            for index, row in df.iterrows():
                try:
                    # 验证和处理数据
                    name = str(row['姓名']).strip()
                    birthday = self._parse_birthday(row['生日'])
                    country = str(row['国家']).strip()
                    gender = str(row['性别']).strip()
                    
                    # 处理Melon注册需要的额外字段
                    email = None
                    email_password = None
                    if has_melon_fields:
                        email = str(row['邮箱']).strip() if '邮箱' in row and pd.notna(row['邮箱']) else None
                        email_password = str(row['邮箱密钥']).strip() if '邮箱密钥' in row and pd.notna(row['邮箱密钥']) else None
                    
                    # 验证数据有效性
                    if not name or name == 'nan':
                        continue  # 跳过空姓名
                    
                    if not birthday:
                        continue  # 跳过无效生日
                    
                    if not country or country == 'nan':
                        country = 'China'  # 默认国家
                    
                    if not gender or gender == 'nan':
                        gender = '男'  # 默认性别
                    
                    # 添加到用户数据列表
                    user_info = {
                        'name': name,
                        'birthday': birthday,
                        'country': country,
                        'gender': gender
                    }
                    
                    # 如果有Melon字段，添加到用户信息中
                    if has_melon_fields:
                        user_info['email'] = email
                        user_info['email_password'] = email_password
                    self.user_data.append(user_info)
                    
                except Exception as e:
                    print(f"处理第{index+1}行数据时出错: {e}")
                    continue
            
            return len(self.user_data) > 0
            
        except Exception as e:
            print(f"导入Excel文件失败: {e}")
            return False
    
    def _parse_birthday(self, birthday_value) -> str:
        """
        解析生日数据
        :param birthday_value: 生日值（可能是字符串、日期对象等）
        :return: 格式化的生日字符串 YYYY-MM-DD
        """
        try:
            if pd.isna(birthday_value):
                return None
            
            # 如果是字符串
            if isinstance(birthday_value, str):
                # 尝试多种日期格式
                date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%d-%m-%Y']
                for fmt in date_formats:
                    try:
                        date_obj = datetime.strptime(birthday_value.strip(), fmt)
                        return date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        continue
            
            # 如果是pandas的Timestamp或datetime对象
            elif hasattr(birthday_value, 'strftime'):
                return birthday_value.strftime('%Y-%m-%d')
            
            return None
            
        except Exception:
            return None
    
    def get_user_data(self) -> List[Dict]:
        """
        获取导入的用户数据
        :return: 用户数据列表
        """
        return self.user_data.copy()
    
    def get_user_count(self) -> int:
        """
        获取导入的用户数量
        :return: 用户数量
        """
        return len(self.user_data)
    
    def clear_data(self):
        """
        清空导入的数据
        """
        self.user_data.clear()
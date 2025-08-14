#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建Melon注册Excel模板文件
"""

import pandas as pd
import os

def create_melon_template():
    """
    创建Melon注册所需的Excel模板文件
    """
    # 创建Melon注册模板数据
    template_data = {
        '姓名': ['张三', '李四', '王五'],
        '生日': ['1990-01-01', '1991-02-02', '1992-03-03'],
        '国家': ['China', 'China', 'China'],
        '性别': ['男', '女', '男'],
        '邮箱': ['example1@gmail.com', 'example2@gmail.com', 'example3@gmail.com'],
        '邮箱密钥': ['your_email_password1', 'your_email_password2', 'your_email_password3']
    }
    
    df = pd.DataFrame(template_data)
    
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(current_dir, 'Melon平台注册数据导入模板.xlsx')
    
    # 保存Excel文件
    df.to_excel(template_path, index=False)
    
    print(f'✅ Melon注册模板文件已创建: {template_path}')

    
    return template_path

if __name__ == '__main__':
    create_melon_template()
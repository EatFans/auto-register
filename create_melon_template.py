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
    template_path = os.path.join(current_dir, 'melon_template.xlsx')
    
    # 保存Excel文件
    df.to_excel(template_path, index=False)
    
    print(f'✅ Melon注册模板文件已创建: {template_path}')
    print('\n模板文件包含以下字段:')
    print('- 姓名: 用户真实姓名')
    print('- 生日: 格式为 YYYY-MM-DD')
    print('- 国家: 用户所在国家')
    print('- 性别: 男/女')
    print('- 邮箱: 用于注册的邮箱地址')
    print('- 邮箱密钥: 邮箱的登录密码，用于获取验证码')
    print('\n请根据实际情况修改模板中的示例数据。')
    
    return template_path

if __name__ == '__main__':
    create_melon_template()
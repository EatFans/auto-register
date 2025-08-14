#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Melon注册功能集成测试
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from register.register_factory import RegisterManagerFactory
from util.import_util import UserDataImporter

def test_melon_registration():
    """
    测试Melon注册功能
    """
    print("=== Melon注册功能集成测试 ===")
    
    # 1. 测试工厂模式是否能创建Melon管理器
    try:
        available_websites = RegisterManagerFactory.get_available_websites()
        print(f"可用网站: {available_websites}")
        
        if 'Melon' not in available_websites:
            print("❌ Melon网站未在工厂中注册")
            return False
        
        # 创建Melon管理器
        def log_callback(msg, color):
            print(f"[{color}] {msg}")
        
        melon_manager = RegisterManagerFactory.create_manager('Melon', log_callback=log_callback)
        print("✅ Melon管理器创建成功")
        
        # 2. 测试配置验证
        config_valid = melon_manager.validate_config()
        print(f"配置验证结果: {config_valid}")
        
        # 3. 测试用户数据导入器是否支持Melon字段
        importer = UserDataImporter()
        
        # 创建测试Excel数据
        import pandas as pd
        test_data = {
            '姓名': ['张三', '李四'],
            '生日': ['1990-01-01', '1991-02-02'],
            '国家': ['China', 'China'],
            '性别': ['男', '女'],
            '邮箱': ['test1@example.com', 'test2@example.com'],
            '邮箱密钥': ['password1', 'password2']
        }
        
        df = pd.DataFrame(test_data)
        test_excel_path = '/tmp/test_melon_data.xlsx'
        df.to_excel(test_excel_path, index=False)
        
        # 导入测试数据
        import_success = importer.import_from_excel(test_excel_path)
        if import_success:
            print("✅ 测试数据导入成功")
            user_data = importer.get_user_data()
            print(f"导入的用户数据: {user_data}")
            
            # 检查是否包含Melon需要的字段
            first_user = user_data[0] if user_data else {}
            if 'email' in first_user and 'email_password' in first_user:
                print("✅ 用户数据包含Melon所需的邮箱和邮箱密钥字段")
            else:
                print("❌ 用户数据缺少Melon所需的字段")
                return False
        else:
            print("❌ 测试数据导入失败")
            return False
        
        # 清理测试文件
        if os.path.exists(test_excel_path):
            os.remove(test_excel_path)
        
        print("\n=== 集成测试完成 ===")
        print("✅ Melon注册功能已成功集成到应用程序中")
        print("\n注意事项:")
        print("1. 确保Excel文件包含以下字段: 姓名、生日、国家、性别、邮箱、邮箱密钥")
        print("2. Melon注册仅支持导入数据模式，不支持随机生成模式")
        print("3. 邮箱密钥用于登录邮箱获取验证码")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_melon_registration()
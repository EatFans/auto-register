#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册机测试脚本
用于测试完整的注册流程是否正常工作
"""

from register.register import RegisterManager
from datetime import datetime
import time

def test_single_registration():
    """
    测试单个账号注册流程
    """
    print("=" * 50)
    print("开始测试单个账号注册流程")
    print("=" * 50)
    
    # 创建注册管理器
    register_manager = RegisterManager()
    
    # 测试参数
    domain = "gmail.com"
    count = 1
    name = ""  # 空字符串表示随机生成
    birthday = "1990-01-01"
    country = "中国"
    gender = "男"
    export_path = f"测试注册结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    thread_count = 1
    
    print(f"测试参数:")
    print(f"  邮箱域名: {domain}")
    print(f"  注册数量: {count}")
    print(f"  姓名: {'随机生成' if not name else name}")
    print(f"  生日: {birthday}")
    print(f"  国家: {country}")
    print(f"  性别: {gender}")
    print(f"  导出路径: {export_path}")
    print(f"  线程数: {thread_count}")
    print()
    
    try:
        # 执行注册
        register_manager.register_accounts_random(
            domain=domain,
            count=count,
            name=name,
            birthday=birthday,
            country=country,
            gender=gender,
            export_path=export_path,
            thread_count=thread_count
        )
        print("\n测试完成！")
        
    except Exception as e:
        print(f"\n测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

def test_import_registration():
    """
    测试导入数据模式注册流程
    """
    print("=" * 50)
    print("开始测试导入数据模式注册流程")
    print("=" * 50)
    
    # 创建注册管理器
    register_manager = RegisterManager()
    
    # 模拟导入的用户数据
    user_data = [
        {
            'name': '张三',
            'birthday': '1990-01-01',
            'country': '中国',
            'gender': '男'
        },
        {
            'name': '李四',
            'birthday': '1992-05-15',
            'country': '中国',
            'gender': '女'
        }
    ]
    
    # 测试参数
    domain = "gmail.com"
    export_path = f"测试导入注册结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    thread_count = 1
    
    print(f"测试参数:")
    print(f"  邮箱域名: {domain}")
    print(f"  用户数据: {len(user_data)} 条")
    print(f"  导出路径: {export_path}")
    print(f"  线程数: {thread_count}")
    print()
    
    for i, user in enumerate(user_data, 1):
        print(f"  用户{i}: {user['name']}, {user['birthday']}, {user['country']}, {user['gender']}")
    print()
    
    try:
        # 执行注册
        register_manager.register_accounts_import(
            domain=domain,
            user_data=user_data,
            export_path=export_path,
            thread_count=thread_count
        )
        print("\n测试完成！")
        
    except Exception as e:
        print(f"\n测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

def test_api_functions():
    """
    测试API函数的基本功能
    """
    print("=" * 50)
    print("开始测试API函数基本功能")
    print("=" * 50)
    
    from api.yes24_register_api import RegistrationManager as APIRegistrationManager
    
    test_email = "test@gmail.com"
    
    try:
        with APIRegistrationManager() as api_manager:
            print(f"测试邮箱验证功能: {test_email}")
            
            # 测试邮箱验证
            verify_result = api_manager.verify_email_only(test_email)
            print(f"邮箱验证结果: {verify_result}")
            

    except Exception as e:
        print(f"API测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """
    主测试函数
    """
    print("注册机系统测试")
    print("=" * 60)
    print("本测试将验证注册机的各项功能是否正常工作")
    print("注意: 测试过程中会发送真实的网络请求")
    print("=" * 60)
    print()
    
    # 询问用户要进行哪些测试
    print("请选择要进行的测试:")
    print("1. API函数基本功能测试")
    print("2. 单个账号注册流程测试")
    print("3. 导入数据模式注册测试")
    print("4. 全部测试")
    print("0. 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (0-4): ").strip()
            
            if choice == '0':
                print("退出测试")
                break
            elif choice == '1':
                test_api_functions()
                break
            elif choice == '2':
                test_single_registration()
                break
            elif choice == '3':
                test_import_registration()
                break
            elif choice == '4':
                test_api_functions()
                print("\n" + "="*30 + "\n")
                time.sleep(2)
                test_single_registration()
                print("\n" + "="*30 + "\n")
                time.sleep(2)
                test_import_registration()
                break
            else:
                print("无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n\n测试被用户中断")
            break
        except Exception as e:
            print(f"输入处理错误: {str(e)}")

if __name__ == '__main__':
    main()
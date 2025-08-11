#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册API交互式测试
模拟完整的浏览器会话操作，包括手动邮箱验证步骤
"""

import sys
import os
import json
import time
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.register_api import (
    RegistrationSession, 
    RegistrationManager,
    verify_email_address,
    activation_email,
    access_registration_form,
    register
)


class InteractiveRegistrationTest:
    """
    交互式注册测试类
    模拟用户在浏览器中的完整操作流程
    """
    
    def __init__(self):
        self.session_manager = None
        self.test_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'surname': 'Test',
            'firstname': 'User',
            'nation': 82,  # 韩国
            'birth': '19900101',
            'gender': 'm'
        }
    
    def print_separator(self, title: str):
        """打印分隔线"""
        print("\n" + "="*60)
        print(f" {title} ")
        print("="*60)
    
    def print_response_info(self, response_data: Dict[str, Any], step_name: str):
        """打印响应信息"""
        print(f"\n[{step_name}] 响应信息:")
        print(f"状态码: {response_data.get('status_code', 'N/A')}")
        print(f"响应内容: {response_data.get('result', 'N/A')[:200]}...")
        print(f"Cookie数量: {len(response_data.get('cookies', {}))}")
        
        # 如果是JSON响应，尝试解析并美化输出
        try:
            result_text = response_data.get('result', '')
            if result_text.strip().startswith('{'):
                json_data = json.loads(result_text)
                print(f"JSON响应: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
        except:
            pass
    
    def get_user_input(self, prompt: str, default: str = None) -> str:
        """获取用户输入"""
        if default:
            user_input = input(f"{prompt} (默认: {default}): ").strip()
            return user_input if user_input else default
        else:
            return input(f"{prompt}: ").strip()
    
    def setup_test_data(self):
        """设置测试数据"""
        self.print_separator("设置测试数据")
        print("请输入测试用的注册信息:")
        
        self.test_data['email'] = self.get_user_input(
            "邮箱地址", self.test_data['email']
        )
        self.test_data['password'] = self.get_user_input(
            "密码", self.test_data['password']
        )
        self.test_data['surname'] = self.get_user_input(
            "姓氏", self.test_data['surname']
        )
        self.test_data['firstname'] = self.get_user_input(
            "名字", self.test_data['firstname']
        )
        self.test_data['birth'] = self.get_user_input(
            "生日(YYYYMMDD)", self.test_data['birth']
        )
        
        gender_choice = self.get_user_input(
            "性别 (m/f)", self.test_data['gender']
        )
        self.test_data['gender'] = gender_choice.lower()
        
        print("\n测试数据设置完成:")
        for key, value in self.test_data.items():
            if key == 'password':
                print(f"{key}: {'*' * len(value)}")
            else:
                print(f"{key}: {value}")
    
    def test_step_1_initialize_session(self):
        """步骤1: 初始化会话"""
        self.print_separator("步骤1: 初始化会话")
        
        self.session_manager = RegistrationManager()
        response = self.session_manager.reg_session.initialize_session()
        
        result_data = {
            'status_code': response.status_code,
            'result': f"页面标题检查: {'FnSignUp' in response.text}",
            'cookies': self.session_manager.reg_session.get_cookies_dict()
        }
        
        self.print_response_info(result_data, "初始化会话")
        
        if response.status_code == 200:
            print("✅ 会话初始化成功")
            return True
        else:
            print("❌ 会话初始化失败")
            return False
    
    def test_step_2_verify_email(self):
        """步骤2: 验证邮箱"""
        self.print_separator("步骤2: 验证邮箱")
        
        print(f"正在验证邮箱: {self.test_data['email']}")
        result_data = self.session_manager.verify_email_only(self.test_data['email'])
        
        self.print_response_info(result_data, "邮箱验证")
        
        # 检查响应是否成功
        if result_data['status_code'] == 200:
            try:
                response_json = json.loads(result_data['result'])
                if response_json.get('ResultCode') == '00':
                    print("✅ 邮箱验证成功，验证邮件已发送")
                    return True
                else:
                    print(f"❌ 邮箱验证失败: {response_json.get('ResultMsg', '未知错误')}")
                    return False
            except json.JSONDecodeError:
                print("❌ 响应格式错误")
                return False
        else:
            print("❌ 邮箱验证请求失败")
            return False
    
    def test_step_3_manual_email_verification(self):
        """步骤3: 手动邮箱验证"""
        self.print_separator("步骤3: 手动邮箱验证")
        
        print(f"请检查邮箱 {self.test_data['email']} 中的验证邮件")
        print("在验证邮件中找到激活链接，复制其中的 'k' 参数值")
        print("例如: https://ticket.yes24.com/Pages/English/Member/FnMyAuthentication.aspx?k=XXXXXX")

        k_token = input("\n请输入邮件中的k参数值: ").strip()
        
        if not k_token:
            print("❌ k参数不能为空")
            return False
        
        print(f"\n正在激活邮箱，k参数: {k_token}")
        result_data = self.session_manager.activate_email_only(
            self.test_data['email'], k_token
        )
        
        self.print_response_info(result_data, "邮箱激活")
        
        # 检查激活是否成功
        if result_data['status_code'] == 200:
            if "Authentication success" in result_data['result']:
                print("✅ 邮箱激活成功")
                return True
            else:
                print("❌ 邮箱激活失败，请检查k参数是否正确")
                return False
        else:
            print("❌ 邮箱激活请求失败")
            return False
    
    def test_step_4_access_registration_form(self):
        """步骤4: 访问注册表单页面"""
        self.print_separator("步骤4: 访问注册表单页面")
        
        session = self.session_manager.reg_session.get_session()
        response = access_registration_form(session)
        
        result_data = {
            'status_code': response.status_code,
            'result': f"表单页面检查: {'FnSignupReg' in response.text}",
            'cookies': self.session_manager.reg_session.get_cookies_dict()
        }
        
        self.print_response_info(result_data, "访问注册表单")
        
        if response.status_code == 200 and 'FnSignupReg' in response.text:
            print("✅ 注册表单页面访问成功")
            self.session_manager.reg_session.form_accessed = True
            return True
        else:
            print("❌ 注册表单页面访问失败")
            return False
    
    def test_step_5_submit_registration(self):
        """步骤5: 提交注册表单"""
        self.print_separator("步骤5: 提交注册表单")
        
        print("正在提交注册信息...")
        print(f"邮箱: {self.test_data['email']}")
        print(f"姓名: {self.test_data['surname']} {self.test_data['firstname']}")
        
        result_data = self.session_manager.register_only(
            email=self.test_data['email'],
            password=self.test_data['password'],
            surname=self.test_data['surname'],
            firstname=self.test_data['firstname'],
            nation=self.test_data['nation'],
            birth=self.test_data['birth'],
            gender=self.test_data['gender']
        )
        
        self.print_response_info(result_data, "提交注册")
        
        # 检查注册结果
        if result_data['status_code'] == 200:
            try:
                response_json = json.loads(result_data['result'])
                result_code = response_json.get('ResultCode')
                result_msg = response_json.get('ResultMsg', '')
                
                if result_code == '00':
                    print("✅ 注册成功！")
                    return True
                elif result_code == '01' and "Your information is not found" in result_msg:
                    print("❌ 注册失败: 会话信息丢失，这正是我们要避免的错误")
                    print("   这表明会话管理有问题，需要检查Cookie和会话状态")
                    return False
                else:
                    print(f"❌ 注册失败: {result_msg}")
                    return False
            except json.JSONDecodeError:
                print("❌ 注册响应格式错误")
                return False
        else:
            print("❌ 注册请求失败")
            return False
    
    def run_complete_test(self):
        """运行完整测试流程"""
        print("🚀 开始注册API交互式测试")
        print("这个测试将模拟完整的浏览器会话操作")
        
        try:
            # 设置测试数据
            self.setup_test_data()
            
            # 步骤1: 初始化会话
            if not self.test_step_1_initialize_session():
                return False
            
            # 步骤2: 验证邮箱
            if not self.test_step_2_verify_email():
                return False
            
            # 步骤3: 手动邮箱验证
            if not self.test_step_3_manual_email_verification():
                return False
            
            # 步骤4: 访问注册表单页面
            if not self.test_step_4_access_registration_form():
                return False
            
            # 等待用户确认
            input("\n按回车键继续提交注册表单...")
            
            # 步骤5: 提交注册表单
            if not self.test_step_5_submit_registration():
                return False
            
            self.print_separator("测试完成")
            print("🎉 所有测试步骤都成功完成！")
            print("✅ 会话状态保持正确，避免了'Your information is not found'错误")
            return True
            
        except KeyboardInterrupt:
            print("\n\n⚠️  测试被用户中断")
            return False
        except Exception as e:
            print(f"\n\n❌ 测试过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # 清理资源
            if self.session_manager:
                self.session_manager.reg_session.close()
                print("\n🧹 会话资源已清理")
    
    def run_quick_test(self):
        """运行快速测试（跳过交互步骤）"""
        print("⚡ 开始快速API测试（仅测试接口连通性）")
        
        try:
            # 初始化会话
            self.session_manager = RegistrationManager()
            response = self.session_manager.reg_session.initialize_session()
            
            if response.status_code == 200:
                print("✅ 会话初始化成功")
                
                # 测试邮箱验证接口
                result = self.session_manager.verify_email_only("test@example.com")
                print(f"✅ 邮箱验证接口响应: {result['status_code']}")
                
                # 测试访问注册表单
                session = self.session_manager.reg_session.get_session()
                form_response = access_registration_form(session)
                print(f"✅ 注册表单访问响应: {form_response.status_code}")
                
                print("\n🎉 快速测试完成，所有接口连通性正常")
                return True
            else:
                print("❌ 会话初始化失败")
                return False
                
        except Exception as e:
            print(f"❌ 快速测试失败: {str(e)}")
            return False
        finally:
            if self.session_manager:
                self.session_manager.reg_session.close()


def main():
    """主函数"""
    print("注册API测试工具")
    print("1. 完整交互式测试（推荐）")
    print("2. 快速连通性测试")
    
    choice = input("\n请选择测试类型 (1/2): ").strip()
    
    tester = InteractiveRegistrationTest()
    
    if choice == '2':
        success = tester.run_quick_test()
    else:
        success = tester.run_complete_test()
    
    if success:
        print("\n✅ 测试成功完成")
        return 0
    else:
        print("\n❌ 测试失败")
        return 1


if __name__ == "__main__":
    exit(main())
#!/usr/bin/env python3
"""
创建用户数据导入模板Excel文件
"""

from openpyxl import Workbook
import os

def create_user_data_template():
    """
    创建用户数据导入模板
    """
    # 创建工作簿
    wb = Workbook()
    ws = wb.active
    ws.title = "用户数据"
    
    # 设置表头
    headers = ['姓名', '生日', '国家', '性别']
    ws.append(headers)
    
    # 添加示例数据
    sample_data = [
        ['张三', '1990-01-15', 'China', '男'],
        ['李四', '1992-05-20', 'China', '女'],
        ['王五', '1988-12-03', 'China', '男'],
        ['赵六', '1995-07-08', 'China', '女'],
        ['John Smith', '1991-03-12', 'USA', '男'],
        ['Jane Doe', '1993-09-25', 'USA', '女'],
        ['山田太郎', '1989-11-18', 'Japan', '男'],
        ['佐藤花子', '1994-04-30', 'Japan', '女']
    ]
    
    for row_data in sample_data:
        ws.append(row_data)
    
    # 设置列宽
    ws.column_dimensions['A'].width = 15  # 姓名
    ws.column_dimensions['B'].width = 12  # 生日
    ws.column_dimensions['C'].width = 10  # 国家
    ws.column_dimensions['D'].width = 8   # 性别
    
    # 添加说明工作表
    ws_info = wb.create_sheet("使用说明")
    instructions = [
        ['用户数据导入模板使用说明'],
        [''],
        ['1. 文件格式要求：'],
        ['   - 文件格式：Excel (.xlsx 或 .xls)'],
        ['   - 必须包含以下列：姓名、生日、国家、性别'],
        [''],
        ['2. 数据格式要求：'],
        ['   - 姓名：真实姓名，不能为空'],
        ['   - 生日：格式为 YYYY-MM-DD，如：1990-01-15'],
        ['   - 国家：国家名称，如：China、USA、Japan等'],
        ['   - 性别：男 或 女'],
        [''],
        ['3. 注意事项：'],
        ['   - 请确保数据的真实性和准确性'],
        ['   - 生日格式必须严格按照 YYYY-MM-DD 格式'],
        ['   - 空行或无效数据将被自动跳过'],
        ['   - 建议先用少量数据测试'],
        [''],
        ['4. 示例数据：'],
        ['   请参考"用户数据"工作表中的示例数据格式']
    ]
    
    for instruction in instructions:
        ws_info.append(instruction)
    
    # 设置说明工作表的列宽
    ws_info.column_dimensions['A'].width = 50
    
    # 保存文件
    template_path = os.path.join(os.path.dirname(__file__), 'Yes24平台注册数据导入模板.xlsx')
    wb.save(template_path)
    print(f"用户数据导入模板已创建：{template_path}")
    return template_path

if __name__ == '__main__':
    create_user_data_template()
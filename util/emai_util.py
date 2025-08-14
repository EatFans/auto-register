from bs4 import BeautifulSoup
import re

def extract_k_value(html_content):
    """
    解析k的值
    :param html_content: html内容
    :return: 返回k的值
    """
    soup = BeautifulSoup(html_content, "html.parser")
    # 查找所有 a 标签的 href
    for a_tag in soup.find_all("a", href=True):
        match = re.search(r"[?&]k=([a-zA-Z0-9\-]+)", a_tag["href"])
        if match:
            return match.group(1)

    # 如果 HTML 结构太乱，直接用正则全局搜索
    match = re.search(r"[?&]k=([a-zA-Z0-9\-]+)", html_content)
    if match:
        return match.group(1)

    return None

def extract_melon_code_value(html_content):
    """
    解析获取melon邮件code验证码
    :param html_content: HTML邮件内容
    :return: 返回6位数字验证码，如果未找到则返回None
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 查找包含验证码的td标签，通常验证码会在特定样式的td中
    # 根据提供的HTML结构，验证码在一个居中显示、绿色字体的td中
    for td_tag in soup.find_all("td"):
        # 检查td标签的style属性是否包含text-align:center和绿色字体
        style = td_tag.get("style", "")
        if "text-align:center" in style and "#00cd3c" in style:
            text = td_tag.get_text(strip=True)
            # 验证是否为6位数字
            if text.isdigit() and len(text) == 6:
                return text
    
    # 如果上述方法未找到，使用正则表达式在整个HTML中搜索6位连续数字
    # 优先查找在td标签中的6位数字
    td_pattern = r'<td[^>]*>\s*(\d{6})\s*</td>'
    match = re.search(td_pattern, html_content, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # 最后尝试查找任何6位连续数字（作为备用方案）
    digit_pattern = r'\b(\d{6})\b'
    match = re.search(digit_pattern, html_content)
    if match:
        return match.group(1)
    
    return None
    
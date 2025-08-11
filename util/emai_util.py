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
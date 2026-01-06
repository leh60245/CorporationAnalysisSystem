"""Markdown 테이블 변환 테스트"""
import sys
sys.path.insert(0, 'C:/Users/kkh60/PycharmProjects/CorporationAnalysis')

from bs4 import BeautifulSoup
from src.core.dart_agent import DartReportAgent

html = """
<table>
    <tr><th>구분</th><th>2024년</th><th>2023년</th></tr>
    <tr><td>매출액</td><td>100억</td><td>80억</td></tr>
    <tr><td>영업이익</td><td>20억</td><td>15억</td></tr>
</table>
"""

soup = BeautifulSoup(html, 'html.parser')
table = soup.find('table')

agent = DartReportAgent()
markdown, metadata = agent.convert_table_to_markdown(table)

# 파일로 저장하여 확인
with open('scripts/markdown_output.txt', 'w', encoding='utf-8') as f:
    f.write("=== Markdown 테이블 ===\n")
    f.write(markdown)
    f.write("\n\n=== repr() ===\n")
    f.write(repr(markdown))
    f.write("\n\n=== 메타데이터 ===\n")
    f.write(str(metadata))

print("Output saved to scripts/markdown_output.txt")

# 각 문자의 ord 값 확인
print("\nFirst 50 characters with ord values:")
for i, char in enumerate(markdown[:50]):
    print(f"  [{i}] '{char}' = {ord(char)}")


import urllib.request
import re

# 尝试获取每周统计页面 - 这个应该有连续的每日数据
url = 'https://az24.vn/thong-ke-giai-dac-biet-theo-tuan.html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')
print(f'HTML length: {len(html)}')

# 查找特定结构: 表格中有日期和对应的特等奖号码
# 从页面结构看, 应该有类似:
# Thứ 2 | Thứ 3 | ... | Chủ nhật 的表头
# 然后每行是一周的数据

# 找包含tuần (周) 的表格
# 保存整个HTML来分析
with open('full_page.txt', 'w', encoding='utf-8') as f:
    f.write(html)
print('Saved full HTML to full_page.txt')

# 尝试找特等奖数据
# 格式可能是: <td class="gdb-cell">68</td> 或类似
patterns = [
    r'class="gdb[^"]*"[^>]*>(\d{2})',
    r'<td[^>]*>(\d{2,5})</td>',
    r'bold[^>]*>(\d{3,5})\s*<span[^>]*>(\d{2})',
]

for i, p in enumerate(patterns):
    matches = re.findall(p, html)[:20]
    print(f'Pattern {i+1}: {len(matches)} matches')
    print(f'  Samples: {matches[:5]}')

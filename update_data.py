#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动更新XSMB数据脚本
由GitHub Actions每天自动运行
"""

import json
import urllib.request
from datetime import datetime

def fetch_today_data():
    """从API获取今天的开奖数据"""
    url = 'https://api-xsmb-today.onrender.com/api/v1'
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response = urllib.request.urlopen(req, timeout=30)
        data = json.loads(response.read().decode('utf-8'))
        
        if data and 'results' in data and 'ĐB' in data['results']:
            date_str = data['time']  # 格式: DD-MM-YYYY
            parts = date_str.split('-')
            formatted_date = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
            
            special_prize = int(data['results']['ĐB'][0])
            last_two = special_prize % 100
            
            return {'d': formatted_date, 'n': last_two}
    except Exception as e:
        print(f"API获取失败: {e}")
    
    return None

def update_historical_data():
    """更新historical_data.json"""
    # 读取现有数据
    with open('historical_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"当前数据条数: {len(data)}")
    print(f"最新日期: {data[0]['d']}")
    
    # 获取今天的数据
    new_data = fetch_today_data()
    
    if new_data:
        print(f"获取到新数据: {new_data['d']} -> {new_data['n']}")
        
        # 检查是否已存在
        existing_dates = {item['d'] for item in data}
        
        if new_data['d'] not in existing_dates:
            data.insert(0, new_data)
            data.sort(key=lambda x: x['d'], reverse=True)
            
            # 保存更新后的数据
            with open('historical_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            
            print(f"✅ 数据已更新! 新增: {new_data['d']}")
            return True
        else:
            print(f"数据已是最新 ({new_data['d']})")
            return False
    else:
        print("❌ 获取新数据失败")
        return False

def regenerate_html():
    """重新生成index.html"""
    import subprocess
    result = subprocess.run(['python', 'generate_html.py'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ index.html 已重新生成")
    else:
        print(f"❌ 生成HTML失败: {result.stderr}")

if __name__ == '__main__':
    print("=" * 50)
    print(f"XSMB数据自动更新 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    updated = update_historical_data()
    
    if updated:
        regenerate_html()
    
    print("=" * 50)

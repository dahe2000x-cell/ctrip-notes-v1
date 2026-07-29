#!/usr/bin/env python3
"""自检脚本：字数/禁词/格式/结构/城市去重"""
import json
import re
import os

BASE = "/Users/chengxinxin/WorkBuddy/2026-07-27-00-39-29"

# 读取所有最近7天的笔记文件
all_notes = []
for f in ["notes_20260726.json", "notes_20260727.json", "notes_20260728.json", "notes_20260729.json"]:
    fp = os.path.join(BASE, f)
    if os.path.exists(fp):
        with open(fp, "r") as fh:
            all_notes.extend(json.load(fh))

# 统计各账号最近7天使用的城市
account_cities = {}
for note in all_notes:
    acc = note.get("account", "")
    city = note.get("city", "")
    if acc not in account_cities:
        account_cities[acc] = set()
    account_cities[acc].add(city)

print("最近7天城市使用记录:")
for acc, cities in account_cities.items():
    print(f"  {acc}: {sorted(cities)}")

# 读取新生成的笔记
with open(os.path.join(BASE, "notes_20260730.json"), "r") as f:
    posts = json.load(f)

# 禁词列表
forbidden_words = [
    "**", "我刚回来", "我亲测", "我上次去", "去了N次", "N刷",
    "本地人告诉我", "只有去过才知道", "闺蜜", "学生党", "穷游", "特种兵",
    "暴走", "网红打卡", "出片", "必去", "不去后悔", "全网最全", 
    "全国第一", "一定要去", "闭眼冲", "酸辣冲鼻很上头", "焦香冒油",
    "携程", "美团", "大众点评", "小红书", "抖音", "快手", "微信",
    "支付宝", "高德", "百度", "滴滴",
    "祈福", "灵验", "许愿", "有求必应", "野味", "现杀", "现宰",
    "石板路雨后长了青苔", "下午四点光线斜照最好看",
    "太美了", "太香了", "这里太美了",
]

required_blocks = ["🚄", "📍", "🏨", "🍜", "📸", "💡", "💰"]

print("\n" + "=" * 60)
print("自检报告：notes_20260730.json")
print("=" * 60)

all_pass = True
for post in posts:
    body = post["body"]
    idx = post["idx"]
    account = post["account"]
    city = post["city"]
    words = post["words"]
    strength = post["strength"]
    
    print(f"\n--- [{idx}] {account} | {city} ({strength}级) ---")
    
    # 1. 字数检查
    if idx == 4 and strength == "S":
        status = "✅" if words >= 2200 else "❌"
        print(f"  字数: {words} (S级要求≥2200) {status}")
        if words < 2200:
            all_pass = False
    else:
        status = "✅" if words >= 1500 else "❌"
        print(f"  字数: {words} (要求≥1500) {status}")
        if words < 1500:
            all_pass = False
    
    # 2. 城市去重检查
    acc_set = account_cities.get(account, set())
    if city in acc_set:
        print(f"  ❌ 城市重复! {account} 最近7天已用过 {city}")
        all_pass = False
    else:
        print(f"  ✅ 城市不重复 ({account} 7天内未用{city})")
    
    # 3. 禁词检查
    has_forbidden = []
    for fw in forbidden_words:
        if fw in body:
            has_forbidden.append(fw)
    if has_forbidden:
        print(f"  ❌ 发现禁词: {has_forbidden}")
        all_pass = False
    else:
        print(f"  ✅ 无禁词")
    
    # 4. ** 检查
    if "**" in body:
        print(f"  ❌ 包含 ** 符号!")
        all_pass = False
    else:
        print(f"  ✅ 无**符号")
    
    # 5. 结构检查
    missing = []
    for block in required_blocks:
        if block not in body:
            missing.append(block)
    if missing:
        print(f"  ❌ 缺少结构块: {missing}")
        all_pass = False
    else:
        print(f"  ✅ 结构完整(7/7)")
    
    # 6. 图片标题检查
    it = post["imageTitle"]
    if "｜" not in it:
        print(f"  ⚠️ 图片标题未使用｜竖线分隔")
    else:
        print(f"  ✅ 图片标题使用｜竖线分隔")
    
    # 7. 图片标题无emoji检查
    emoji_in_title = re.findall(r'[\U0001F300-\U0001F9FF\u2600-\u27BF\u2B50\u2708-\u27BF]', it)
    if emoji_in_title:
        print(f"  ❌ 图片标题含emoji: {emoji_in_title}")
        all_pass = False
    else:
        print(f"  ✅ 图片标题无emoji")
    
    # 8. CTA检查
    cta_phrases = ["你从哪个城市出发", "建议先收藏", "你更想看"]
    has_cta = any(p in body for p in cta_phrases)
    if not has_cta:
        print(f"  ❌ 缺少结尾CTA!")
        all_pass = False
    else:
        print(f"  ✅ 有结尾CTA")
    
    # 9. 避坑条数
    pit_count = len(re.findall(r'\d️⃣', body))
    min_pits = 5 if (idx == 4 and strength == "S") else 4
    print(f"  避坑条数: {pit_count}条 (要求≥{min_pits}) {'✅' if pit_count >= min_pits else '❌'}")
    if pit_count < min_pits:
        all_pass = False
    
    # 10. 住宿区域检查
    area_count = len(re.findall(r'暑假¥\d+-\d+', body))
    print(f"  住宿价格锚点: {area_count}个 {'✅' if area_count >= 2 else '❌'}")
    
    # 11. 正文标题emoji检查
    bt = post["bodyTitle"]
    emoji_end = re.findall(r'[\U0001F300-\U0001F9FF\u2600-\u27BF\u2B50\u2708-\u27BF]$', bt)
    if emoji_end:
        print(f"  ✅ 正文标题末尾有城市emoji")
    else:
        print(f"  ⚠️ 正文标题末尾可能没有城市emoji")
    
    # 12. 花费对比锚点
    has_compare = bool(re.search(r'[省節省]¥?\d+|[比对比]', body))
    print(f"  {'✅' if has_compare else '⚠️'} 花费对比锚点 {'有' if has_compare else '可能缺失'}")

print("\n" + "=" * 60)
if all_pass:
    print("✅ 全部通过!")
else:
    print("❌ 存在问题需要修复!")
print("=" * 60)

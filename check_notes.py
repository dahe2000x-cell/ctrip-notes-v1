#!/usr/bin/env python3
"""自检脚本：字数/格式/合规/结构"""
import json
import re

with open("/Users/chengxinxin/WorkBuddy/2026-07-27-00-39-29/notes_20260729.json", "r") as f:
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

# 必须有的结构块
required_blocks = ["🚄", "📍", "🏨", "🍜", "📸", "💡", "💰"]

print("=" * 60)
print("自检报告：notes_20260729.json")
print("=" * 60)

all_pass = True
for post in posts:
    body = post["body"]
    idx = post["idx"]
    account = post["account"]
    city = post["city"]
    words = post["words"]
    
    print(f"\n--- [{idx}] {account} | {city} ---")
    
    # 1. 字数检查
    if idx == 4:
        status = "✅" if words >= 1500 else "❌"
        print(f"  字数: {words} (S级要求1500+) {status}")
    else:
        status = "✅" if 1200 <= words <= 1800 else "⚠️"
        print(f"  字数: {words} (要求1200-1800) {status}")
    if words > 3000:
        print(f"  ❌ 超过3000上限!")
        all_pass = False
    
    # 2. 禁词检查
    has_forbidden = []
    for fw in forbidden_words:
        if fw in body:
            has_forbidden.append(fw)
    if has_forbidden:
        print(f"  ❌ 发现禁词: {has_forbidden}")
        all_pass = False
    else:
        print(f"  ✅ 无禁词")
    
    # 3. ** 检查
    if "**" in body:
        print(f"  ❌ 包含 ** 符号!")
        all_pass = False
    else:
        print(f"  ✅ 无**符号")
    
    # 4. 结构检查
    missing = []
    for block in required_blocks:
        if block not in body:
            missing.append(block)
    if missing:
        print(f"  ❌ 缺少结构块: {missing}")
        all_pass = False
    else:
        print(f"  ✅ 结构完整(7/7)")
    
    # 5. 图片标题检查
    it = post["imageTitle"]
    if "｜" not in it and "|" not in it:
        print(f"  ⚠️ 图片标题未使用竖线分隔")
    else:
        print(f"  ✅ 图片标题使用竖线分隔")
    
    # 6. CTA检查
    cta_phrases = ["你从哪个城市出发", "建议先收藏", "你更想看"]
    has_cta = any(p in body for p in cta_phrases)
    if not has_cta:
        print(f"  ❌ 缺少结尾CTA!")
        all_pass = False
    else:
        print(f"  ✅ 有结尾CTA")
    
    # 7. 住宿区域检查
    price_pattern = re.findall(r'¥\d+-\d+', body)
    print(f"  ✅ 价格锚点: {len(price_pattern)}个")
    
    # 8. 避坑条数
    pit_count = len(re.findall(r'\d️⃣', body))
    print(f"  避坑条数: {pit_count}条 {'✅' if pit_count >= 4 else '❌'}")

print("\n" + "=" * 60)
if all_pass:
    print("✅ 全部通过!")
else:
    print("❌ 存在问题需要修复!")
print("=" * 60)

import json
import re

with open('notes_20260812.json', 'r') as f:
    notes = json.load(f)

print("=" * 60)
print("8/12 携程笔记质量检查")
print("=" * 60)

# 城市去重检查 - 最近7天
past_7_days = {
    '林姐': set(),
    '叮咚': set(),
    '柚柚': set()
}

for day_offset in range(7):
    date = f"202608{5+day_offset:02d}"
    try:
        with open(f'notes_{date}.json', 'r') as f:
            day_notes = json.load(f)
        for n in day_notes:
            account = n.get('account', '')
            city = n.get('city', '')
            if account in past_7_days:
                past_7_days[account].add(city)
    except FileNotFoundError:
        print(f"  文件不存在: notes_{date}.json")
        continue

print("\n最近7天(8/5-8/11)各账号已用城市：")
for account, cities in past_7_days.items():
    if cities:
        print(f"  {account}: {sorted(cities)}")

print("\n" + "=" * 60)
print("逐篇检查")
print("=" * 60)

all_pass = True

for note in notes:
    idx = note['idx']
    account = note['account']
    city = note['city']
    strength = note.get('strength', '')
    body = note['body']
    
    # 1. 城市去重
    if city in past_7_days.get(account, set()):
        print(f"\n[FAIL] 第{idx}篇 {account}/{city} - 城市重复！{account}7天内已用过{city}")
        all_pass = False
        continue
    
    # 2. 字数检查
    # Count Chinese characters
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', body))
    total_chars = len(body)
    
    if strength == 'S':
        min_chars = 2200
    else:
        min_chars = 1500
    
    word_status = "PASS" if chinese_chars >= min_chars else "FAIL"
    if chinese_chars < min_chars:
        all_pass = False
    
    # 3. 格式检查
    has_stars = '**' in body
    star_status = "FAIL" if has_stars else "PASS"
    if has_stars:
        all_pass = False
    
    # 4. 内容块检查
    has_transport = '🚄' in body or '交通' in body
    has_attractions = '📍' in body or '玩什么' in body
    has_hotel = '🏨' in body or '住宿' in body
    has_food = '🍜' in body or '吃' in body
    has_route = '路线' in body or 'Day1' in body
    has_trap = '避坑' in body
    has_tips = 'Tips' in body or '👗' in body
    has_cta = '评论' in body
    has_no_spending = '花费参考' not in body
    
    # Image title check
    has_pipe = '｜' in note.get('imageTitle', '')
    # Body title check - ends with emoji
    body_title = note.get('bodyTitle', '')
    
    print(f"\n第{idx}篇 | {account} | {city} | {strength}级")
    print(f"  中文字数: {chinese_chars} (要求≥{min_chars}) [{word_status}]")
    print(f"  总字符数: {total_chars}")
    print(f"  无**符号: {star_status}")
    print(f"  交通: {'✓' if has_transport else '✗'}")
    print(f"  景点: {'✓' if has_attractions else '✗'}")
    print(f"  住宿: {'✓' if has_hotel else '✗'}")
    print(f"  美食: {'✓' if has_food else '✗'}")
    print(f"  路线: {'✓' if has_route else '✗'}")
    print(f"  避坑: {'✓' if has_trap else '✗'}")
    print(f"  Tips: {'✓' if has_tips else '✗'}")
    print(f"  CTA: {'✓' if has_cta else '✗'}")
    print(f"  无花费参考: {'✓' if has_no_spending else '✗'}")
    print(f"  imageTitle含｜: {'✓' if has_pipe else '✗'}")
    print(f"  bodyTitle: {body_title}")

print("\n" + "=" * 60)
if all_pass:
    print("全部检查通过！")
else:
    print("存在不通过项，需要修正！")
print("=" * 60)

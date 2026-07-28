#!/usr/bin/env python3
"""
携程笔记工作台 - AI正文生成桥接脚本
读取规则文件 + 生成请求，为每篇笔记构造完整生成提示词，输出到文件供AI处理。
"""
import json
import os
import sys
from datetime import datetime, date

OBSIDIAN_BASE = os.path.expanduser("~/Documents/Obsidian Vault/大禾自我探索之旅/2_项目/1_携程笔记")
RULE_FILES = {
    "入口": os.path.join(OBSIDIAN_BASE, "❤️00_入口_携程笔记AI执行说明.md"),
    "选题规则": os.path.join(OBSIDIAN_BASE, "❤️携程笔记_选题规则_v1.md"),
    "写作规范": os.path.join(OBSIDIAN_BASE, "❤️写作规范-提示词.md"),
    "CLAUDE": os.path.join(OBSIDIAN_BASE, "❤️CLAUDE.md"),
}
REQUEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generation_request.json")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_posts")

def read_file(path):
    if not os.path.exists(path):
        return f"[文件不存在: {path}]"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def read_rules():
    rules = {}
    for name, path in RULE_FILES.items():
        rules[name] = read_file(path)
    return rules

def load_request():
    if not os.path.exists(REQUEST_FILE):
        print(f"错误: 未找到生成请求文件 {REQUEST_FILE}")
        print("请先在工作台中点击「请求AI生成正文」按钮。")
        sys.exit(1)
    with open(REQUEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def build_prompt(task, rules):
    """为单篇笔记构造完整的AI生成提示词"""
    t = task
    is_s = t.get("isKey", False)
    
    parts = []
    parts.append("# 携程笔记正文生成任务\n")
    parts.append(f"## 基本信息")
    parts.append(f"- 账号: {t.get('account', '')}")
    parts.append(f"- 篇次: 第{t.get('idx', '')}篇")
    parts.append(f"- 城市: {t.get('city', '')}")
    parts.append(f"- 公式类型: {t.get('formula', '')}")
    parts.append(f"- 选题强度: {t.get('strength', '')}")
    if is_s:
        parts.append(f"- **重点笔记（收益翻倍）**: 正文信息密度必须最高")
    parts.append("")
    
    parts.append(f"## 标题")
    parts.append(f"- 图片标题（封面用，竖线分隔，不用emoji）: {t.get('imageTitle', '')}")
    parts.append(f"- 正文标题（30字内，1个城市相关emoji末位）: {t.get('bodyTitle', '')}")
    parts.append("")
    
    parts.append(f"## 正文控制字段")
    parts.append(f"- 目标人群: {t.get('targetAudience', '')}")
    parts.append(f"- 核心矛盾: {t.get('coreProblem', '')}")
    parts.append(f"- 钱的角度: {t.get('moneyAngle', '')}")
    parts.append(f"- 正文必须写: {t.get('mustWrite', '')}")
    parts.append(f"- 正文禁止写: {t.get('mustNotWrite', '')}")
    parts.append(f"- 天气风险: {t.get('weatherRisk', '')}")
    parts.append("")
    
    parts.append(f"## 图片信息")
    parts.append(f"- 封面图: {t.get('coverImgPath', '未选')}")
    parts.append(f"- 配图数量: {t.get('imageCount', 0)}张")
    parts.append("")
    
    parts.append(f"## 生成要求")
    parts.append("1. 正文1000-1800字" + ("（可写1800字，信息最完整）" if is_s else ""))
    parts.append("2. 开头2句话交付决策+制造反差" + ("，必须包含钱的角度" if is_s else ""))
    parts.append("3. 必须包含7要素: 交通/住宿/路线/避坑/费用/美食/天气提醒")
    parts.append("4. 住宿模块: 2-3个推荐区域+价格区间" + ("+暑假vs淡季对比" if is_s else ""))
    parts.append("5. 避坑指南: 至少4条" + ("（5-6条）" if is_s else "") + "，至少2条当地专属")
    parts.append("6. 美食: 只写店名+菜品+价格，禁用夸张口感词")
    parts.append("7. Tips: 👗👟🌂👴👶📸 格式")
    parts.append("8. 花费参考: 分类列+总数+对比锚点")
    parts.append("9. 结尾: 三选一CTA，必须有评论召唤")
    parts.append("10. 正文标题末尾加1个城市/场景相关emoji")
    parts.append("")
    
    parts.append(f"## 写作规则（全文引用）")
    parts.append(rules.get("写作规范", "[规则文件未找到]"))
    parts.append("")
    
    parts.append(f"## 合规检查规则（全文引用）")
    parts.append(rules.get("CLAUDE", "[规则文件未找到]"))
    parts.append("")
    
    parts.append(f"## 选题规则（全文引用）")
    parts.append(rules.get("选题规则", "[规则文件未找到]"))
    
    return "\n".join(parts)

def main():
    request = load_request()
    tasks = request.get("tasks", [])
    rules = read_rules()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today_str = date.today().strftime("%Y%m%d")
    
    print(f"📋 正在为 {len(tasks)} 篇笔记构造生成提示词...")
    print(f"📁 规则文件: {len([r for r in rules.values() if not r.startswith('[')])}/{len(rules)} 个已加载")
    print()
    
    all_prompts = []
    for i, task in enumerate(tasks):
        if not task.get("city"):
            print(f"  ⚠️  第{i+1}篇: 城市未填写，跳过")
            continue
        
        prompt = build_prompt(task, rules)
        task_label = f"第{task['idx']}篇_{task.get('account','')}_{task.get('city','')}"
        filename = f"{today_str}_{task_label}.md"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(prompt)
        
        all_prompts.append(prompt)
        print(f"  ✓ {task_label} → {filename}")
    
    combined_path = os.path.join(OUTPUT_DIR, f"{today_str}_全部4篇生成提示词.md")
    with open(combined_path, "w", encoding="utf-8") as f:
        f.write("\n\n---\n\n".join(all_prompts))
    
    print(f"\n✅ 已生成 {len(all_prompts)} 篇提示词")
    print(f"📂 输出目录: {OUTPUT_DIR}")
    print(f"📄 合并文件: {combined_path}")
    print()
    print("接下来: 告诉 WorkBuddy 「帮我生成今天的4篇携程笔记正文」")
    print("WorkBuddy 会读取这些提示词和规则文件，生成完整的4篇正文。")

if __name__ == "__main__":
    main()

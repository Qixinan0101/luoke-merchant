"""
洛克王国世界 · 远行商人数据抓取器
从 onebiji.com 抓取实时数据（HTML 解析），输出为 JSON
GitHub Actions 定时运行此脚本

HTML 结构说明：
  <div class="gitem">         ← 图片 + 限购
    <img src="...">
    <em>限购X</em>
  </div>
  <div class="sp-text">       ← 相邻 div，名字 + 价格
    <p><em>商品名</em></p>
    <div><em>价格：XXX</em></div>
  </div>

页面一次性包含所有轮次商品，按轮次顺序排列（每轮3件）
"""
import requests
import re
import json
import os
from datetime import datetime, timezone, timedelta

BEIJING_TZ = timezone(timedelta(hours=8))
SOURCE_URL = "https://www.onebiji.com/hykb_tools/comm/lkwgmerchant/preview.php?id=1&immgj=0"
OUTPUT_FILE = "data/merchant.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

ROUND_TIMES = {1: (8, 12), 2: (12, 16), 3: (16, 20), 4: (20, 24)}
ITEMS_PER_ROUND = 3


def get_current_round():
    now = datetime.now(BEIJING_TZ)
    hour = now.hour
    for rnd, (start, end) in ROUND_TIMES.items():
        if start <= hour < end:
            return rnd
    return None


def fetch_page():
    resp = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    resp.encoding = 'utf-8'
    return resp.text


def parse_all_items(html):
    """
    按位置解析所有商品。
    找出每个 class="gitem" 的位置，向后取 700 字符，
    从中提取图片/限购/名字/价格。
    """
    items = []

    # 找出所有 "class=\"gitem\"" 的位置
    positions = [m.start() for m in re.finditer(r'class="gitem"', html)]

    for pos in positions:
        # 向后取 700 字符作为上下文窗口
        window = html[pos - 5:pos + 700]  # -5 确保 "<div " 被包含

        # 提取限购: <em>限购X</em>（在 gitem div 内）
        limit_match = re.search(r'限购(\d+)', window)
        limit = limit_match.group(1) if limit_match else "?"

        # 提取名字: sp-text 中的 <p><em>名称</em></p>
        name_match = re.search(r'<p[^>]*><em>([^<]+)</em></p>', window)
        if not name_match:
            # 可能是模板占位符（空的 gitem）
            if 'shopName' in window or 'shopimg' in window:
                continue
            name = None
        else:
            name = name_match.group(1).strip()
            if not name or name == '':
                continue  # 空名跳过

        # 提取价格: 价格：XXX
        price_match = re.search(r'价格[：:]\s*(\S+)', window)
        price = price_match.group(1).strip() if price_match else "?"

        # 提取图片
        img_match = re.search(r'<img[^>]*src=["\']([^"\']+)["\']', window)
        image = img_match.group(1) if img_match else None
        if image and image.startswith('//'):
            image = 'https:' + image
        elif image and not image.startswith('http'):
            image = 'https://www.onebiji.com' + image if image.startswith('/') else None

        items.append({
            "name": name,
            "price": price,
            "priceRaw": price,
            "limit": limit,
            "image": image,
            "category": "道具",
            "description": "",
        })

    return items


def group_by_round(items):
    rounds = {"1": [], "2": [], "3": [], "4": []}
    for i, item in enumerate(items):
        rnd = (i // ITEMS_PER_ROUND) + 1
        if rnd <= 4:
            item["round"] = rnd
            rounds[str(rnd)].append(item)
    return rounds


def main():
    now_beijing = datetime.now(BEIJING_TZ)
    print(f"[{now_beijing.strftime('%Y-%m-%d %H:%M:%S')}] 开始抓取...")
    print(f"数据源: {SOURCE_URL}")

    current_round = get_current_round()
    status = "open" if current_round else "closed"
    print(f"北京时间: {now_beijing.strftime('%H:%M')} | 状态: {status} | 当前第{current_round}轮")

    try:
        html = fetch_page()
        print(f"页面: {len(html)} 字符")

        all_items = parse_all_items(html)
        print(f"解析到 {len(all_items)} 件商品:")

        rounds_data = group_by_round(all_items)
        for rnd in ["1", "2", "3", "4"]:
            rd_items = rounds_data[rnd]
            marker = ">>" if str(current_round) == rnd else "  "
            if rd_items:
                names = ", ".join(i["name"] for i in rd_items)
                print(f"  {marker} 第{rnd}轮 ({len(rd_items)}件): {names}")
            else:
                print(f"  {marker} 第{rnd}轮: 无数据")

        current_items = rounds_data.get(str(current_round), []) if current_round else []

        # 计算下次刷新
        round_hours = {1: 8, 2: 12, 3: 16, 4: 20}
        if current_round and current_round < 4:
            next_hour = round_hours[current_round + 1]
            next_refresh = now_beijing.replace(hour=next_hour, minute=0, second=0, microsecond=0)
        else:
            next_refresh = now_beijing.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)

        result = {
            "sourceUrl": SOURCE_URL,
            "fetchedAt": datetime.now(timezone.utc).isoformat(),
            "timezone": "Asia/Shanghai",
            "status": status,
            "round": current_round,
            "nextRefreshBeijing": next_refresh.strftime("%Y-%m-%d %H:%M:%S"),
            "durationHours": 4,
            "merchantPosition": "",
            "items": current_items,
            "rounds": rounds_data
        }

        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n已保存 {OUTPUT_FILE}")
        print(f"当前: 第{current_round}轮 {len(current_items)}件 | 全部: {len(all_items)}件")

        if len(all_items) == 0 and status == "open":
            print("警告: 营业时间但未解析到商品")

    except Exception as e:
        print(f"失败: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()

"""
洛克王国世界 · 远行商人数据抓取器
从 onebiji.com 抓取实时数据（HTML 解析），输出为 JSON
GitHub Actions 定时运行此脚本
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

def get_current_round():
    """根据北京时间计算当前轮次"""
    now = datetime.now(BEIJING_TZ)
    hour = now.hour
    if 8 <= hour < 12:
        return 1
    elif 12 <= hour < 16:
        return 2
    elif 16 <= hour < 20:
        return 3
    elif 20 <= hour < 24:
        return 4
    else:
        return None  # 休息中

def fetch_page():
    """抓取 onebiji.com 页面"""
    resp = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    resp.encoding = 'utf-8'
    return resp.text

def parse_items(html):
    """
    从 HTML 中提取所有商品。
    onebiji.com 页面结构：数据在 div.gitem 中
    格式：
    <div class="gitem">
      <div> <img src="..."> <em>限购X</em> </div>
      <div class="sp-text">
        <p><em>商品名</em></p>
        <div><em>价格：XXX </em></div>
      </div>
    </div>
    """
    items = []

    # 匹配每个 gitem 块
    gitem_pattern = r'<div class="gitem">(.*?)</div>\s*</div>\s*</li>'
    blocks = re.findall(gitem_pattern, html, re.DOTALL)

    for block in blocks:
        # 商品名: <p><em>名称</em></p>
        name_match = re.search(r'<p[^>]*><em>([^<]+)</em></p>', block)
        if not name_match:
            continue
        name = name_match.group(1).strip()

        # 价格: 价格：XXX
        price_match = re.search(r'价格[：:]\s*(\S+)', block)
        price = price_match.group(1).strip() if price_match else "?"

        # 限购: <em>限购X</em>
        limit_match = re.search(r'限购(\d+)', block)
        limit = limit_match.group(1) if limit_match else "?"

        # 图片
        img_match = re.search(r'<img[^>]*src=["\']([^"\']+)["\']', block)
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

def main():
    now_beijing = datetime.now(BEIJING_TZ)
    print(f"[{now_beijing.strftime('%Y-%m-%d %H:%M:%S')}] 开始抓取远行商人数据...")
    print(f"数据源: {SOURCE_URL}")

    current_round = get_current_round()
    status = "open" if current_round else "closed"

    try:
        html = fetch_page()
        print(f"页面抓取成功，长度: {len(html)} 字符")

        items = parse_items(html)
        print(f"解析到 {len(items)} 件商品:")
        for item in items:
            print(f"  - {item['name']} | {item['price']} | 限购{item['limit']}")

        # 组织数据
        rounds_data = {"1": [], "2": [], "3": [], "4": []}
        if current_round and items:
            r_key = str(current_round)
            # 给每个 item 标记轮次
            for item in items:
                item["round"] = current_round
            rounds_data[r_key] = items

        # 计算下次刷新
        round_hours = {1: 8, 2: 12, 3: 16, 4: 20}
        if current_round and current_round < 4:
            next_hour = round_hours[current_round + 1]
            next_refresh = now_beijing.replace(hour=next_hour, minute=0, second=0, microsecond=0)
        else:
            # 次日 8 点
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
            "items": items if status == "open" else [],
            "rounds": rounds_data
        }

        # 保存 JSON
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n数据已保存至 {OUTPUT_FILE}")
        print(f"状态: {status} | 轮次: {current_round} | 商品: {len(items)}件")

        if len(items) == 0 and status == "open":
            print("警告: 营业时间但未解析到商品，可能是页面结构变化")
            # 仍然保存但标记
        elif status == "closed":
            print("远行商人当前休息中 (00:00-08:00)")

    except Exception as e:
        print(f"抓取失败: {e}")
        # 保持已有数据
        if os.path.exists(OUTPUT_FILE):
            print("保留已有数据文件")
        raise  # 让 GitHub Actions 感知失败

if __name__ == "__main__":
    main()

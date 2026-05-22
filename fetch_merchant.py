"""
娲涘厠鐜嬪浗涓栫晫 路 杩滆鍟嗕汉鏁版嵁鎶撳彇鍣?浠?onebiji.com 鎶撳彇瀹炴椂鏁版嵁锛岃緭鍑轰负 JSON
GitHub Actions 瀹氭椂杩愯姝よ剼鏈?"""
import requests
import re
import json
import os
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

BEIJING_TZ = timezone(timedelta(hours=8))
SOURCE_URL = "https://www.onebiji.com/hykb_tools/comm/lkwgmerchant/preview.php?id=1&immgj=0"
OUTPUT_FILE = "data/merchant.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def fetch_page():
    """鎶撳彇 onebiji.com 椤甸潰"""
    resp = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    resp.encoding = 'utf-8'
    return resp.text

def parse_html(html):
    """瑙ｆ瀽 HTML 鎻愬彇鍟嗗搧鏁版嵁"""
    soup = BeautifulSoup(html, 'html.parser')
    now = datetime.now(BEIJING_TZ)
    fetched_at = datetime.now(timezone.utc).isoformat()

    # ===== 鎻愬彇褰撳墠杞鍜岀姸鎬?=====
    status = "open"
    current_round = 1
    round_text = ""

    # 鏌ユ壘杞鏍囪瘑
    # 鍙兘鐨勬ā寮? "绗琗杞?, "round X", 鏁板瓧鏍囪瘑
    for tag in soup.find_all(['span', 'div', 'p', 'h2', 'h3']):
        text = tag.get_text(strip=True)
        m = re.search(r'绗琝s*(\d)\s*杞?, text)
        if m:
            current_round = int(m.group(1))
            round_text = text
            break

    # 妫€鏌ユ槸鍚﹀叧闂?    page_text = soup.get_text()
    if any(keyword in page_text for keyword in ['宸插叧闂?, '浼戞伅涓?, '鏈紑鏀?, '灏氭湭寮€甯?, '鍗冲皢寮€鍚?]):
        status = "closed"

    # ===== 鎻愬彇鍟嗗搧鏁版嵁 =====
    items = []
    rounds_data = {str(i): [] for i in range(1, 5)}

    # 灏濊瘯澶氱鏂瑰紡鎻愬彇鍟嗗搧鍒楄〃
    cards = (
        soup.select('.item-card') or
        soup.select('.merchant-item') or
        soup.select('.goods-item') or
        soup.select('[class*="item"]') or
        soup.select('.card') or
        soup.select('tr[class]')
    )

    # 濡傛灉娌℃湁鎵惧埌鍗＄墖锛屽皾璇曚粠琛ㄦ牸鎻愬彇
    tables = soup.find_all('table')
    if tables and not cards:
        for table in tables:
            rows = table.find_all('tr')[1:]  # skip header
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    item = parse_table_row(cols)
                    if item:
                        items.append(item)
    else:
        # 浠庡崱鐗囦腑鎻愬彇
        for card in cards:
            item = parse_card(card)
            if item and item.get('name'):
                items.append(item)

    # 鎸夎疆娆″垎缁?    for item in items:
        r = item.get('round', current_round)
        r_key = str(r)
        if r_key in rounds_data:
            rounds_data[r_key].append(item)

    # 濡傛灉娌℃湁鎵惧埌鍟嗗搧锛屽皾璇曚粠鏂囨湰涓彁鍙?    if not items:
        items = extract_from_text(page_text)
        for item in items:
            r = item.get('round', current_round)
            r_key = str(r)
            if r_key in rounds_data:
                rounds_data[r_key].append(item)

    # 璁＄畻褰撳墠杞晢鍝?    current_items = rounds_data.get(str(current_round), [])

    # 璁＄畻涓嬫鍒锋柊鏃堕棿
    round_hours = {1: 8, 2: 12, 3: 16, 4: 20}
    if current_round < 4:
        next_hour = round_hours.get(current_round + 1, 8)
    else:
        next_hour = 32  # 娆℃棩8鐐?
    if next_hour >= 24:
        next_refresh = now.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
    else:
        next_refresh = now.replace(hour=next_hour, minute=0, second=0, microsecond=0)

    result = {
        "sourceUrl": SOURCE_URL,
        "fetchedAt": fetched_at,
        "timezone": "Asia/Shanghai",
        "status": status,
        "round": current_round if status != "closed" else None,
        "startedAtBeijing": None,
        "nextRefreshBeijing": next_refresh.strftime("%Y-%m-%d %H:%M:%S"),
        "durationHours": 4,
        "merchantPosition": "",
        "items": current_items if status != "closed" else [],
        "rounds": rounds_data
    }

    return result

def parse_card(card):
    """浠庡崱鐗囧厓绱犱腑鎻愬彇鍟嗗搧淇℃伅"""
    text = card.get_text(' ', strip=True)

    name = None
    price = "?"
    limit = "?"
    category = "鍏朵粬"
    image = None
    item_round = None

    # 鎻愬彇鍥剧墖
    img = card.find('img')
    if img:
        image = img.get('src') or img.get('data-src')

    # 鎻愬彇鍚嶇О
    name_el = (
        card.select_one('.name') or
        card.select_one('.item-name') or
        card.select_one('.title') or
        card.select_one('h3') or
        card.select_one('strong')
    )
    if name_el:
        name = name_el.get_text(strip=True)

    if not name:
        # 灏濊瘯浠庢枃鏈腑鎻愬彇 - 鎵剧湅璧锋潵鍍忓晢鍝佸悕鐨勬枃鏈?        name_matches = re.findall(r'([\u4e00-\u9fff]{2,6}(?:鐞億鏋渱鑽瘄鐭硘绮墊铔媩鐜墊灏榺鏅秥鐝爘鐠億娑?)', text)
        if name_matches:
            name = name_matches[0]

    # 鎻愬彇浠锋牸
    price_matches = re.findall(r'(\d+\.?\d*[wW涓嘳?)', text)
    for pm in price_matches:
        if re.match(r'^\d+', pm):
            price = pm
            break

    # 鎻愬彇闄愯喘
    limit_matches = re.findall(r'闄愯喘\s*(\d+)', text)
    if limit_matches:
        limit = limit_matches[0]
    else:
        limit_matches = re.findall(r'(\d+)\s*涓?, text)
        if limit_matches:
            limit = limit_matches[0]

    # 鎻愬彇鍒嗙被
    categories = ['鐐奸噾鏉愭枡', '绮剧伒鍠傚吇鏉愭枡', '琛€鑴変慨鏀归亾鍏?, '绮剧伒铔?, '鐐僵铔?, '鎶€鑳界煶鏉愭枡', '鍜曞櫆鐞?, '绮剧伒', '閬撳叿']
    for cat in categories:
        if cat in text:
            category = cat
            break

    # 鎻愬彇杞
    round_matches = re.findall(r'[绗疆]\s*(\d)\s*[杞甝', text)
    if round_matches:
        item_round = int(round_matches[0])

    if name:
        return {
            "name": name,
            "price": price,
            "priceRaw": price,
            "limit": limit,
            "image": image,
            "category": category,
            "description": "",
            "round": item_round
        }
    return None

def parse_table_row(cols):
    """浠庤〃鏍艰涓彁鍙栧晢鍝佷俊鎭?""
    name = None
    price = "?"
    limit = "?"
    category = "鍏朵粬"
    image = None

    for col in cols:
        text = col.get_text(strip=True)
        img = col.find('img')
        if img:
            image = img.get('src')

        # 鍚嶇О閫氬父鍦ㄧ涓€涓湁鎰忎箟鐨勫垪
        if not name and len(text) >= 2 and re.search(r'[\u4e00-\u9fff]', text):
            if not re.match(r'^\d', text):
                name = text
                continue

        # 浠锋牸
        if re.match(r'^\d+', text):
            if not price or price == '?':
                price = text
                continue

        # 闄愯喘
        if re.match(r'^\d+$', text) and price != '?':
            limit = text
            continue

        # 鍒嗙被
        categories = ['鐐奸噾鏉愭枡', '绮剧伒鍠傚吇鏉愭枡', '琛€鑴変慨鏀归亾鍏?, '绮剧伒铔?, '鐐僵铔?, '鎶€鑳界煶鏉愭枡', '鍜曞櫆鐞?]
        for cat in categories:
            if cat in text:
                category = cat
                break

    if name:
        return {
            "name": name,
            "price": price,
            "priceRaw": price,
            "limit": limit,
            "image": image,
            "category": category,
            "description": "",
            "round": None
        }
    return None

def extract_from_text(text):
    """浠庣函鏂囨湰涓敖鍙兘鎻愬彇鍟嗗搧淇℃伅"""
    items = []
    # 鎸夎鍒嗗壊
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        # 鏌ユ壘鍟嗗搧鍚嶇О妯″紡
        name_match = re.search(r'([\u4e00-\u9fff]{2,8}(?:鐞億鏋渱鑽瘄鐭硘绮墊铔媩鐜墊灏榺鏅秥鐝爘鐠億娑瞸鍓倈涓竱涔?)', line)
        if not name_match:
            continue

        name = name_match.group(1)
        # 鍦ㄥ悓琛屾垨鍚庣画琛屾壘浠锋牸
        price = "?"
        limit = "?"
        category = "鍏朵粬"

        price_match = re.search(r'(\d+\.?\d*[wW涓嘳?)', line)
        if not price_match and i + 1 < len(lines):
            price_match = re.search(r'(\d+\.?\d*[wW涓嘳?)', lines[i + 1])
        if price_match:
            price = price_match.group(1)

        limit_match = re.search(r'闄愯喘\s*(\d+)', line)
        if limit_match:
            limit = limit_match.group(1)

        categories = ['鐐奸噾鏉愭枡', '绮剧伒鍠傚吇鏉愭枡', '琛€鑴変慨鏀归亾鍏?, '绮剧伒铔?, '鐐僵铔?, '鎶€鑳界煶鏉愭枡', '鍜曞櫆鐞?]
        for cat in categories:
            if cat in line:
                category = cat
                break

        items.append({
            "name": name,
            "price": price,
            "priceRaw": price,
            "limit": limit,
            "image": None,
            "category": category,
            "description": "",
            "round": None
        })

    return items

def main():
    print(f"[{datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')}] 寮€濮嬫姄鍙栬繙琛屽晢浜烘暟鎹?..")
    print(f"鏁版嵁婧? {SOURCE_URL}")

    try:
        html = fetch_page()
        print(f"椤甸潰鎶撳彇鎴愬姛锛岄暱搴? {len(html)} 瀛楃")

        data = parse_html(html)
        print(f"瑙ｆ瀽瀹屾垚:")
        print(f"  鐘舵€? {data['status']}")
        print(f"  杞: {data['round']}")
        print(f"  鍟嗗搧鎬绘暟: {sum(len(v) for v in data['rounds'].values())}")
        for r, items in data['rounds'].items():
            if items:
                print(f"  绗瑊r}杞? {len(items)}浠?)
                for item in items:
                    print(f"    - {item['name']} ({item['price']})")

        # 淇濆瓨 JSON
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n鏁版嵁宸蹭繚瀛樿嚦 {OUTPUT_FILE}")

    except Exception as e:
        print(f"鎶撳彇澶辫触: {e}")
        # 涓嶉€€鍑洪潪闆剁姸鎬佺爜锛屼繚鎸佸凡鏈夋暟鎹笉鍙?        if os.path.exists(OUTPUT_FILE):
            print("淇濈暀宸叉湁鏁版嵁鏂囦欢")

if __name__ == "__main__":
    main()

import csv, re, sys, json, time
from html import unescape
try:
    import requests
except ImportError:
    print("請在 GitHub Actions 中安裝 requests")
    sys.exit(1)

KEYS = {
    "stroller": [r"嬰兒車(租借|出借|借用)", r"推車(租借|借用)"],
    "nursing":  [r"(哺|集)乳室", r"育嬰室", r"親子(室|空間)"],
    "diaper":   [r"尿布(檯|台|臺)", r"換尿布台"],
    "hotwater": [r"(熱水|熱開水|飲水機|溫奶|沖泡)"],
    "elevator": [r"(電梯|無障礙(電梯|設施|通道))"],
    "queue":    [r"(博愛(服務|禮遇)|孕婦(優先|禮遇)|親子(優先|禮遇))"],
    "play":     [r"(兒童遊戲|親子遊戲|遊戲區|遊戲室|Kids? ?Zone)"]
}

TIMEOUT = 15
HEADERS = {"User-Agent":"Mozilla/5.0 (compatible; FriendlyBot/1.0)"}

def fetch(url):
    if not url: return ""
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        return r.text
    except Exception:
        return ""

def detect(html, pats):
    if not html: return None
    t = unescape(html)
    for p in pats:
        if re.search(p, t, re.I):
            return True
    return None  # 未知

def main(csv_in, csv_out, json_out):
    rows = list(csv.DictReader(open(csv_in, newline="", encoding="utf-8-sig")))
    for i, row in enumerate(rows, 1):
        html = fetch(row.get("services_url") or row.get("homepage_url") or "")
        for key, pats in KEYS.items():
            cur = (row.get(key) or "").strip()
            if cur in ("有","無","1","0","true","false","True","False"):  # 保留人工
                row[key] = "有" if cur in ("有","1","true","True") else "無"
                continue
            val = detect(html, pats)
            row[key] = "有" if val else ""  # None/False 一律未知
        time.sleep(0.3)
    # 回寫 out.csv
    with open(csv_out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    # 轉 json
    import subprocess
    subprocess.check_call([sys.executable, "csv_to_facilities_json.py", csv_out, json_out])

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python scrape_facilities.py tw_dept_master_template.csv out.csv facilities.json")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])

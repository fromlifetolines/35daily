import csv, json, sys

def to_bool(v):
    v = (v or "").strip()
    if v in ("有","Y","y","1","true","True"): return True
    if v in ("無","N","n","0","false","False"): return False
    return None

def main(csv_in, json_out):
    with open(csv_in, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    data = []
    for r in rows:
        indicators = {k: to_bool(r.get(k)) for k in ("stroller","nursing","diaper","hotwater","elevator","queue","play")}
        data.append({
            "name": f"{(r.get('chain','') or '').strip()} {(r.get('branch','') or '').strip()}".strip(),
            "region": r.get("region",""),
            "city": r.get("city",""),
            "address": r.get("address",""),
            "category": r.get("category","百貨商場"),
            "source": r.get("services_url") or r.get("homepage_url") or "",
            "indicators": indicators
        })
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python csv_to_facilities_json.py out.csv facilities.json")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])

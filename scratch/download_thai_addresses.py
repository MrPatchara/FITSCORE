import urllib.request
import json
import os

url = "https://raw.githubusercontent.com/kongvut/thai-province-data/master/api/latest/province_with_district_and_sub_district.json"

try:
    print(f"Downloading from {url}...")
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
        data = json.loads(content)
        
    print(f"Successfully downloaded. Rows: {len(data)}")
    
    compact = {}
    for p in data:
        p_name = p.get('name_th', '').strip()
        if not p_name:
            continue
        compact[p_name] = {}
        
        # Districts list
        districts = p.get('districts') or []
        for d in districts:
            d_name = d.get('name_th', '').strip()
            if not d_name:
                continue
            compact[p_name][d_name] = {}
            
            # Sub-districts list
            sub_districts = d.get('sub_districts') or d.get('subdistrict') or d.get('tambons') or []
            for sd in sub_districts:
                sd_name = sd.get('name_th', '').strip()
                zip_code = str(sd.get('zip_code', '')).strip()
                if not sd_name:
                    continue
                compact[p_name][d_name][sd_name] = zip_code

    out_dir = r"c:\Github\FITSCORE\app\resources"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "thai_addresses.json")
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(compact, f, ensure_ascii=False, indent=2)
        
    print(f"Compact file written successfully to {out_path}")
    print(f"File size: {os.path.getsize(out_path) / 1024:.2f} KB")

except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()

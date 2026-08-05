import json
from pathlib import Path

root = Path(__file__).parent

with open(root / 'data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

missing = []
for key, rel_path in data.items():
    full_path = Path("E:\\Programs\\TaikoNijiiroDondaEX Ver4.1\\TaikoNijiiroDondaEX Ver4.1\\Songs") / rel_path
    if not full_path.exists():
        missing.append((key, rel_path))

if missing:
    print(f"{len(missing)} missing paths out of {len(data)} total:\n")
    for key, rel_path in missing:
        print(f"  [{key}] {rel_path}")
else:
    print(f"All {len(data)} paths exist.")

import json

for b in [1, 2, 3]:
    with open(f"raw_data/TEST 1 - ETS 2023/part3_batch{b}.json", "r", encoding="utf-8") as f:
        d = json.load(f)
    print(f"Batch {b}: {len(d.get('groups', []))} groups")
    for g in d.get('groups', []):
        qs = [q['question_number'] for q in g.get('questions', [])]
        print(f"  Group {g.get('id')}: {len(qs)} questions: {qs}")

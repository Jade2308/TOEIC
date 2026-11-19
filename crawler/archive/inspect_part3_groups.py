import json

with open('raw_data/TEST 1 - ETS 2023/part3_whisper_raw.json', 'r', encoding='utf-8') as f:
    segs = json.load(f)

# Find group indices
group_starts = [
    (32, 34, 5),
    (35, 37, 15),
    (38, 40, 24),
    (41, 43, 33),
    (44, 46, 43),
    (47, 49, 52),
    (50, 52, 61),
    (53, 55, 70),
    (56, 58, 79),
    (59, 61, 88),
    (62, 64, 96),
    (65, 67, 107),
    (68, 70, 118),
    (71, 73, 128) # End marker (Part 4)
]

for i in range(len(group_starts) - 1):
    q_start, q_end, idx = group_starts[i]
    next_idx = group_starts[i+1][2]
    # Check if there is "Go on to next page" before next_idx
    sub = segs[idx:next_idx]
    
    t_start = sub[0]['start']
    t_end = sub[-1]['end']
    
    # Filter out "Go on to the next page" if it's the last segment
    if 'go on to' in sub[-1]['text'].lower():
        t_end = sub[-2]['end']
    
    print(f"Group {q_start}-{q_end} (segs {idx}..{next_idx}): {t_start:.1f}s -> {t_end:.1f}s (dur {t_end-t_start:.1f}s)")
    for s in sub:
        print(f"    [{s['start']:06.1f}s - {s['end']:06.1f}s]: {s['text']}")
    print("-" * 60)

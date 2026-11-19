import json

with open("scripts/all_audio_words.json", "r", encoding="utf-8") as f:
    words = json.load(f)

# Helper to find word by condition
def find_word_idx(cond, start_time=0.0):
    for i, w in enumerate(words):
        if w["start"] >= start_time and cond(w, i):
            return i
    return None

# ==========================================
# PART 1 (Q1 to Q6)
# ==========================================
# Q1: "Number 1. Look at the picture..." starts ~101.5s. Before that is Part 1 directions.
# Q2: "Number 2. Look at..." starts ~123.0s
# Q3: "Go on to the next page" -> "Number 3. Look at..." starts ~155.8s
# Q4: "Number 4. Look at..." starts ~180.0s
# Q5: "Number 5. Look at..." starts ~201.5s
# Q6: "Go on to the next page" -> "Number 6. Look at..." starts ~232.8s
# Part 2 directions start at ~268.0s
p1_ranges = {
    1: (101.5, 122.8),
    2: (122.8, 155.5),
    3: (155.5, 179.8),
    4: (179.8, 201.2),
    5: (201.2, 232.5),
    6: (232.5, 267.5),
}

# ==========================================
# PART 2 (Q7 to Q31)
# ==========================================
p2_ranges = {
    7:  (293.0, 315.5),
    8:  (315.5, 336.0),
    9:  (336.0, 356.0),
    10: (356.0, 376.0),
    11: (376.0, 396.0),
    12: (396.0, 415.7),
    13: (415.7, 436.3),
    14: (436.3, 455.8),
    15: (455.8, 477.0),
    16: (477.0, 497.3),
    17: (497.3, 517.6),
    18: (517.6, 538.4),
    19: (538.4, 556.5),
    20: (556.5, 575.1),
    21: (575.1, 596.7),
    22: (596.7, 617.9),
    23: (617.9, 638.9),
    24: (638.9, 659.3),
    25: (659.3, 678.4),
    26: (678.4, 700.1),
    27: (700.1, 720.8),
    28: (720.8, 742.1),
    29: (742.1, 762.1),
    30: (762.1, 780.9),
    31: (780.9, 802.1),
}

# ==========================================
# PART 3 (13 groups)
# ==========================================
# P3 g32_34: starts at 832.0s
# P3 g35_37: starts at 905.5s
# P3 g38_40: starts at 980.5s
# P3 g41_43: starts at 1054.0s
# P3 g44_46: starts at 1132.5s
# P3 g47_49: starts at 1216.5s
# P3 g50_52: starts at 1295.5s
# P3 g53_55: starts at 1366.5s
# P3 g56_58: starts at 1446.0s
# P3 g59_61: starts at 1524.0s
# P3 g62_64: starts at 1606.8s
# P3 g65_67: starts at 1697.0s
# P3 g68_70: starts at 1782.0s
# Part 4 directions start at ~1872.0s
p3_ranges = {
    "g32_34": (832.0, 905.5),
    "g35_37": (905.5, 980.5),
    "g38_40": (980.5, 1054.0),
    "g41_43": (1054.0, 1132.5),
    "g44_46": (1132.5, 1216.5),
    "g47_49": (1216.5, 1295.5),
    "g50_52": (1295.5, 1366.5),
    "g53_55": (1366.5, 1446.0),
    "g56_58": (1446.0, 1524.0),
    "g59_61": (1524.0, 1606.8),
    "g62_64": (1606.8, 1697.0),
    "g65_67": (1697.0, 1782.0),
    "g68_70": (1782.0, 1872.0),
}

# ==========================================
# PART 4 (10 groups)
# ==========================================
# P4 g71_73: starts at 1901.5s
# P4 g74_76: starts at 1981.5s
# P4 g77_79: starts at 2065.0s
# P4 g80_82: starts at 2138.5s
# P4 g83_85: starts at 2233.8s
# P4 g86_88: starts at 2318.0s
# P4 g89_91: starts at 2398.0s
# P4 g92_94: starts at 2475.5s
# P4 g95_97: starts at 2555.0s
# P4 g98_100: starts at 2646.0s
# Audio ends ~2735.0s
p4_ranges = {
    "g71_73": (1901.5, 1981.5),
    "g74_76": (1981.5, 2065.0),
    "g77_79": (2065.0, 2138.5),
    "g80_82": (2138.5, 2233.8),
    "g83_85": (2233.8, 2318.0),
    "g86_88": (2318.0, 2398.0),
    "g89_91": (2398.0, 2475.5),
    "g92_94": (2475.5, 2555.0),
    "g95_97": (2555.0, 2646.0),
    "g98_100": (2646.0, 2735.0),
}

all_data = {
    "part1": p1_ranges,
    "part2": p2_ranges,
    "part3": p3_ranges,
    "part4": p4_ranges,
}

with open("scripts/exact_audio_ranges.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2)

print("Exact audio ranges compiled successfully for all 54 slices!")

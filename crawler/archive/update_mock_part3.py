import json
import re

with open("raw_data/TEST 1 - ETS 2023/test1_part3.json", "r", encoding="utf-8") as f:
    p3_data = json.load(f)

groups = p3_data["question_groups"]
questions = p3_data["questions"]

print(f"Loaded {len(groups)} groups and {len(questions)} questions")

# Format groups as TypeScript
groups_ts = []
for g in groups:
    segs_ts = []
    for s in g.get("transcript_segments", []):
        segs_ts.append(f"""      {{
        id: {json.dumps(s["id"], ensure_ascii=False)},
        speaker: {json.dumps(s["speaker"], ensure_ascii=False)},
        start_time: {s["start_time"]},
        end_time: {s["end_time"]},
        text_en: {json.dumps(s["text_en"], ensure_ascii=False)},
        text_vi: {json.dumps(s["text_vi"], ensure_ascii=False)},
        is_trap: {'true' if s.get('is_trap') else 'false'},
      }},""")
    
    segs_str = "\n".join(segs_ts)
    img_str = json.dumps(g['image_url'], ensure_ascii=False) if g.get("image_url") else "null"
    
    groups_ts.append(f"""  {{
    id: {json.dumps(g["id"], ensure_ascii=False)},
    test_name: {json.dumps(g["test_name"], ensure_ascii=False)},
    part: {g["part"]},
    image_url: {img_str},
    audio_url: {json.dumps(g["audio_url"], ensure_ascii=False)},
    passage_text: null,
    transcript_segments: [
{segs_str}
    ],
  }},""")

groups_code = "\n".join(groups_ts)

# Format questions as TypeScript
questions_ts = []
for q in questions:
    ev_str = json.dumps(q['evidence_quote'], ensure_ascii=False) if q.get("evidence_quote") else "null"
    
    if q.get("paraphrase_pair"):
        para_str = f"""{{
      original: {json.dumps(q['paraphrase_pair']['original'], ensure_ascii=False)},
      paraphrased: {json.dumps(q['paraphrase_pair']['paraphrased'], ensure_ascii=False)},
    }}"""
    else:
        para_str = "null"

    questions_ts.append(f"""  {{
    id: {json.dumps(q["id"], ensure_ascii=False)},
    group_id: {json.dumps(q["group_id"], ensure_ascii=False)},
    part: {q["part"]},
    question_number: {q["question_number"]},
    question_type_tag: {json.dumps(q["question_type_tag"], ensure_ascii=False)},
    question_text: {json.dumps(q["question_text"], ensure_ascii=False)},
    options: {{
      A: {json.dumps(q["options"]["A"], ensure_ascii=False)},
      B: {json.dumps(q["options"]["B"], ensure_ascii=False)},
      C: {json.dumps(q["options"]["C"], ensure_ascii=False)},
      D: {json.dumps(q["options"]["D"], ensure_ascii=False)},
    }},
    correct_answer: {json.dumps(q["correct_answer"], ensure_ascii=False)},
    evidence_quote: {ev_str},
    paraphrase_pair: {para_str},
    explanation_vi: {json.dumps(q["explanation_vi"], ensure_ascii=False)},
  }},""")

questions_code = "\n".join(questions_ts)

with open("src/data/mock_toeic_data.ts", "r", encoding="utf-8") as f:
    content = f.read()

# Replace PART 3 groups
pattern_group = r"  // -+\n  // PART 3[^\n]+\n  // -+\n[\s\S]*?(?=  // -+\n  // PART 4 - QUESTIONS 9)"

replacement_group = f"""  // ----------------------------------------------------------------------------
  // PART 3 - QUESTIONS 32 TO 70 (13 Conversation Groups, 39 Questions)
  // ----------------------------------------------------------------------------
{groups_code}

"""

if re.search(pattern_group, content):
    content = re.sub(pattern_group, replacement_group, content, count=1)
    print("Replaced Part 3 groups successfully!")
else:
    print("Could not match Part 3 groups pattern!")

# Replace PART 3 questions
pattern_q = r"  // -+\n  // PART 3[^\n]+\n  // -+\n[\s\S]*?(?=  // -+\n  // PART 4 \(3 questions\))"

replacement_q = f"""  // ----------------------------------------------------------------------------
  // PART 3 - QUESTIONS 32 TO 70 (39 Questions)
  // ----------------------------------------------------------------------------
{questions_code}

"""

if re.search(pattern_q, content):
    content = re.sub(pattern_q, replacement_q, content, count=1)
    print("Replaced Part 3 questions successfully!")
else:
    print("Could not match Part 3 questions pattern!")

with open("src/data/mock_toeic_data.ts", "w", encoding="utf-8") as f:
    f.write(content)

print("mock_toeic_data.ts written successfully!")

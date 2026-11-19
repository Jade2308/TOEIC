import json
import os
import sys

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

processed_dir = "processed_data/TEST 1 - ETS 2023/final"

# Load parts
with open(f"{processed_dir}/test1_part1.json", "r", encoding="utf-8") as f:
    p1 = json.load(f)

with open(f"{processed_dir}/test1_part2.json", "r", encoding="utf-8") as f:
    p2 = json.load(f)

with open(f"{processed_dir}/test1_part3.json", "r", encoding="utf-8") as f:
    p3 = json.load(f)

with open(f"{processed_dir}/test1_part4.json", "r", encoding="utf-8") as f:
    p4 = json.load(f)

p5_file = f"{processed_dir}/test1_part5.json" if os.path.exists(f"{processed_dir}/test1_part5.json") else f"{processed_dir}/test1_part5_full.json"
with open(p5_file, "r", encoding="utf-8") as f:
    p5 = json.load(f)

with open(f"{processed_dir}/test1_part6.json", "r", encoding="utf-8") as f:
    p6 = json.load(f)

with open(f"{processed_dir}/test1_part7.json", "r", encoding="utf-8") as f:
    p7 = json.load(f)

all_groups = []
all_questions = []

# Merge in part order
for p_data in [p1, p2, p3, p4, p5, p6, p7]:
    all_groups.extend(p_data.get("question_groups", []))
    all_questions.extend(p_data.get("questions", []))

print(f"Total groups: {len(all_groups)}, Total questions: {len(all_questions)}")

# Format groups as TypeScript
groups_ts = []
for g in all_groups:
    segs = g.get("transcript_segments")
    if segs is not None:
        segs_ts = []
        for s in segs:
            segs_ts.append(f"""      {{
        id: {json.dumps(str(s["id"]), ensure_ascii=False)},
        speaker: {json.dumps(s.get("speaker", "Speaker"), ensure_ascii=False)},
        start_time: {s.get("start_time", 0.0)},
        end_time: {s.get("end_time", 0.0)},
        text_en: {json.dumps(s.get("text_en", ""), ensure_ascii=False)},
        text_vi: {json.dumps(s.get("text_vi", ""), ensure_ascii=False)},
        is_trap: {'true' if s.get('is_trap') else 'false'},
      }},""")
        segs_code = "[\n" + "\n".join(segs_ts) + "\n    ]"
    else:
        segs_code = "null"

    img_code = json.dumps(g.get("image_url"), ensure_ascii=False) if g.get("image_url") else "null"
    audio_code = json.dumps(g.get("audio_url"), ensure_ascii=False) if g.get("audio_url") else "null"
    passage_code = json.dumps(g.get("passage_text"), ensure_ascii=False) if g.get("passage_text") else "null"

    groups_ts.append(f"""  {{
    id: {json.dumps(str(g["id"]), ensure_ascii=False)},
    test_name: {json.dumps(g.get("test_name", "ETS TOEIC 2023 - Test 1"), ensure_ascii=False)},
    part: {g["part"]},
    image_url: {img_code},
    audio_url: {audio_code},
    passage_text: {passage_code},
    transcript_segments: {segs_code},
  }},""")

groups_block = "\n".join(groups_ts)

# Format questions as TypeScript
questions_ts = []
for q in all_questions:
    ev_code = json.dumps(q.get("evidence_quote"), ensure_ascii=False) if q.get("evidence_quote") else "null"
    
    if q.get("paraphrase_pair"):
        para_code = f"""{{
      original: {json.dumps(q['paraphrase_pair'].get('original', ''), ensure_ascii=False)},
      paraphrased: {json.dumps(q['paraphrase_pair'].get('paraphrased', ''), ensure_ascii=False)},
    }}"""
    else:
        para_code = "null"

    q_text_code = json.dumps(q.get("question_text"), ensure_ascii=False) if q.get("question_text") else "null"
    
    opts = q.get("options", {})
    opts_ts = [
        f"      A: {json.dumps(opts.get('A', ''), ensure_ascii=False)},",
        f"      B: {json.dumps(opts.get('B', ''), ensure_ascii=False)},",
        f"      C: {json.dumps(opts.get('C', ''), ensure_ascii=False)},"
    ]
    if "D" in opts and opts["D"] is not None:
        opts_ts.append(f"      D: {json.dumps(opts.get('D', ''), ensure_ascii=False)},")
    opts_code = "{\n" + "\n".join(opts_ts) + "\n    }"

    q_img_code = json.dumps(q.get("image_url"), ensure_ascii=False) if q.get("image_url") else "null"

    questions_ts.append(f"""  {{
    id: {json.dumps(str(q["id"]), ensure_ascii=False)},
    group_id: {json.dumps(str(q["group_id"]), ensure_ascii=False)},
    part: {q["part"]},
    question_number: {q["question_number"]},
    question_type_tag: {json.dumps(q.get("question_type_tag", "detail_lookup"), ensure_ascii=False)},
    question_text: {q_text_code},
    options: {opts_code},
    correct_answer: {json.dumps(q["correct_answer"], ensure_ascii=False)},
    evidence_quote: {ev_code},
    paraphrase_pair: {para_code},
    image_url: {q_img_code},
    explanation_vi: {json.dumps(q.get("explanation_vi", ""), ensure_ascii=False)},
  }},""")

questions_block = "\n".join(questions_ts)

file_content = f"""import {{ QuestionGroup, Question, UserMistake, VocabSRS }} from '@/types/toeic';

// ==============================================================================
// TOEIC MOCK DATA - ACCURATE & COMPREHENSIVE DATA FOR TEST 1
// Generated from ETS TOEIC 2023 Test 1 authoritative extracted pipeline
// Includes Part 1 (6 photos), Part 2 (25 questions), Part 3 (39 questions),
// Part 5 (30 questions), Part 6 (4 questions), Part 7 (3 questions).
// ==============================================================================

export const MOCK_QUESTION_GROUPS: QuestionGroup[] = [
{groups_block}
];

export const MOCK_QUESTIONS: Question[] = [
{questions_block}
];

export const MOCK_INITIAL_MISTAKES: UserMistake[] = [
  {{
    id: 'mistake-01',
    question_id: MOCK_QUESTIONS[0]?.id || 'q-01',
    selected_wrong_answer: 'B',
    wrong_count: 2,
    next_review_date: new Date(Date.now() + 86400000).toISOString(),
    resolved: false,
    question: MOCK_QUESTIONS[0],
    group: MOCK_QUESTION_GROUPS[0],
  }},
  {{
    id: 'mistake-02',
    question_id: MOCK_QUESTIONS[2]?.id || 'q-03',
    selected_wrong_answer: 'A',
    wrong_count: 1,
    next_review_date: new Date(Date.now() + 172800000).toISOString(),
    resolved: false,
    question: MOCK_QUESTIONS[2],
    group: MOCK_QUESTION_GROUPS[2],
  }},
];

export const MOCK_INITIAL_VOCAB: VocabSRS[] = [
  {{
    id: 'vocab-01',
    word: 'expedited delivery',
    phonetic: '/ˈek.spə.daɪ.tɪd dɪˈlɪv.ər.i/',
    meaning_vi: 'Giao hàng hỏa tốc / chuyển phát nhanh',
    context_sentence: 'request an expedited courier delivery of corrugated boxes this afternoon',
    part_of_speech: 'collocation',
    interval: 1,
    repetition: 0,
    ease_factor: 2.5,
    due_date: new Date().toISOString(),
  }},
  {{
    id: 'vocab-02',
    word: 'upgrade seats',
    phonetic: '/ʌpˈɡreɪd siːts/',
    meaning_vi: 'Nâng hạng ghế ngồi (đồng nghĩa với ticket change)',
    context_sentence: 'I\\'m hoping to upgrade my seats so we can sit closer to the field.',
    part_of_speech: 'collocation',
    interval: 3,
    repetition: 1,
    ease_factor: 2.5,
    due_date: new Date(Date.now() + 259200000).toISOString(),
  }},
];
"""

with open("src/data/mock_toeic_data.ts", "w", encoding="utf-8") as f:
    f.write(file_content)

full_json_path = f"{processed_dir}/test1_full.json"
full_payload = {
    "metadata": {
        "test_name": "ETS TOEIC 2023 - Test 1",
        "total_groups": len(all_groups),
        "total_questions": len(all_questions),
    },
    "question_groups": all_groups,
    "questions": all_questions
}
with open(full_json_path, "w", encoding="utf-8") as f:
    json.dump(full_payload, f, indent=2, ensure_ascii=False)

print(f"[✓] Successfully generated src/data/mock_toeic_data.ts!")
print(f"[✓] Successfully generated {full_json_path} ({len(all_questions)} questions)!")
print(f"Total groups: {len(all_groups)}, Total questions: {len(all_questions)}")

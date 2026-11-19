import json
import os
import sys
import uuid

# Import groups and questions
from build_part7_final import part7_groups
from build_part7_questions import part7_questions

print(f"Total groups: {len(part7_groups)}")
print(f"Total questions: {len(part7_questions)}")

# Load official answers for verification
ans_file = "processed_data/TEST 1 - ETS 2023/intermediate/answers/Dap-an-test-1-ets-2023.answers.json"
with open(ans_file, encoding="utf-8") as f:
    official_answers = json.load(f)

# Convert all string IDs to deterministic UUIDs for Supabase PostgreSQL compatibility
ns = uuid.NAMESPACE_DNS
group_id_map = {}

for g in part7_groups:
    old_id = g["id"]
    new_uuid = str(uuid.uuid5(ns, f"ets2023-test1-p7-{old_id}"))
    group_id_map[old_id] = new_uuid
    g["id"] = new_uuid

for q in part7_questions:
    old_gid = q["group_id"]
    q["group_id"] = group_id_map[old_gid]
    q["id"] = str(uuid.uuid5(ns, f"ets2023-test1-q{q['question_number']}"))

# Verification checks
errors = []

# Check question numbers
q_numbers = [q["question_number"] for q in part7_questions]
expected_numbers = list(range(147, 201))
if q_numbers != expected_numbers:
    errors.append(f"Question numbers do not match expected 147-200. Found: {q_numbers}")

# Check answer keys
for q in part7_questions:
    num = str(q["question_number"])
    expected_ans = official_answers.get(num)
    if q["correct_answer"] != expected_ans:
        errors.append(f"Question {num}: answer '{q['correct_answer']}' does not match official '{expected_ans}'")

# Check group references
group_ids = {g["id"] for g in part7_groups}
for q in part7_questions:
    if q["group_id"] not in group_ids:
        errors.append(f"Question {q['question_number']} has unknown group_id {q['group_id']}")

# Check evidence quotes against passage texts
groups_by_id = {g["id"]: g["passage_text"] for g in part7_groups}
for q in part7_questions:
    ev = q.get("evidence_quote")
    if ev:
        passage = groups_by_id[q["group_id"]]
        if ev not in passage:
            print(f"[WARN] Question {q['question_number']}: Quote '{ev}' not found verbatim in group {q['group_id']}")

if errors:
    print("\n[VALIDATION FAILED]:")
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)
else:
    print("\n[✓] All 54 questions and 15 groups passed verification with deterministic UUIDs!")

output_payload = {
    "metadata": {
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 7,
        "total_groups": len(part7_groups),
        "total_questions": len(part7_questions),
        "updated_at": "2026-10-31"
    },
    "question_groups": part7_groups,
    "questions": part7_questions
}

out_file = "processed_data/TEST 1 - ETS 2023/final/test1_part7.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(output_payload, f, indent=2, ensure_ascii=False)

print(f"\n[✓] Successfully saved complete Part 7 dataset to {out_file}")

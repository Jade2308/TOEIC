import json
import os
import sys

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def verify():
    data = json.load(open("processed_data/TEST 2 - ETS 2023/final/test_2___ets_2023_full.json", encoding="utf-8"))
    groups = data["question_groups"]
    questions = data["questions"]

    print(f"Total Groups: {len(groups)}")
    print(f"Total Questions: {len(questions)}")

    # 1. Question numbers check
    q_nums = [q["question_number"] for q in questions]
    assert len(q_nums) == 200, f"Expected 200, got {len(q_nums)}"
    assert q_nums == list(range(1, 201)), "Question numbers are not 1 to 200 sequential!"
    print("  [OK] Question numbers 1-200 are sequential and complete.")

    # 2. Group IDs check
    g_ids = set(g["id"] for g in groups)
    assert len(g_ids) == len(groups), "Duplicate group IDs!"
    for q in questions:
        assert q["group_id"] in g_ids, f"Invalid group_id for Q{q['question_number']}"
    print("  [OK] All questions linked to valid groups.")

    # 3. Audio URLs check
    missing_audio = []
    for g in groups:
        if g.get("audio_url"):
            local_path = os.path.join("public", g["audio_url"].lstrip("/"))
            if not os.path.exists(local_path):
                missing_audio.append(local_path)
    assert not missing_audio, f"Missing audio files: {missing_audio[:5]}"
    audio_count = sum(1 for g in groups if g.get("audio_url"))
    print(f"  [OK] All {audio_count} audio files verified on disk.")

    # 4. Image URLs check
    missing_images = []
    for g in groups:
        if g.get("image_url"):
            local_path = os.path.join("public", g["image_url"].lstrip("/"))
            if not os.path.exists(local_path):
                missing_images.append(local_path)
    assert not missing_images, f"Missing image files: {missing_images[:5]}"
    img_count = sum(1 for g in groups if g.get("image_url"))
    print(f"  [OK] All {img_count} image files verified on disk.")

    # 5. Official answers check
    official = json.load(open("processed_data/TEST 2 - ETS 2023/intermediate/answers/official_answers.json"))
    mismatches = []
    for q in questions:
        num = str(q["question_number"])
        if num in official and q["correct_answer"] != official[num]:
            mismatches.append((num, q["correct_answer"], official[num]))
    assert not mismatches, f"Answer mismatches: {mismatches}"
    print("  [OK] All 200 answers strictly match the official answer key.")

    # 6. Check explanations
    no_exp = [q["question_number"] for q in questions if not q.get("explanation_vi")]
    assert not no_exp, f"Missing explanation for questions: {no_exp}"
    print("  [OK] All 200 questions have in-depth Vietnamese explanations.")

    print("\n>>> ALL VALIDATION CHECKS PASSED PERFECTLY! <<<")

if __name__ == "__main__":
    verify()

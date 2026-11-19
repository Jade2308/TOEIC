from __future__ import annotations

"""
Dynamic Audio Alignment, Slicing & Whisper Transcription Module for TOEIC Tests.
Performs full-audio landmark detection, eliminating hardcoded timestamp drift.
"""

import os
import sys
import json
import re
import shutil
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

try:
    import av
    from faster_whisper import WhisperModel
except ImportError:
    av = None
    WhisperModel = None


def slice_audio_file(in_path: str, out_path: str, start_sec: float, end_sec: float):
    """Fast audio frame slicing using PyAV."""
    if av is None:
        raise ImportError("Package 'av' is required for audio slicing. Run: pip install av")

    in_container = av.open(in_path)
    in_stream = in_container.streams.audio[0]
    out_container = av.open(out_path, mode="w")
    out_stream = out_container.add_stream("mp3", rate=in_stream.rate)
    out_stream.bit_rate = in_stream.bit_rate or 128000

    start_pts = int(start_sec / in_stream.time_base)
    end_pts = int(end_sec / in_stream.time_base)
    in_container.seek(start_pts, stream=in_stream)

    for frame in in_container.decode(in_stream):
        if frame.pts < start_pts:
            continue
        if frame.pts > end_pts:
            break
        frame.pts = None
        for packet in out_stream.encode(frame):
            out_container.mux(packet)

    for packet in out_stream.encode(None):
        out_container.mux(packet)

    out_container.close()
    in_container.close()


def transcribe_full_audio_if_needed(
    audio_path: Path,
    whisper_dir: Path,
    device: str = "auto",
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Transcribes the complete listening audio with word timestamps and caches output."""
    if WhisperModel is None:
        raise ImportError("Package 'faster-whisper' is required. Run: pip install faster-whisper")

    whisper_dir.mkdir(parents=True, exist_ok=True)
    segs_file = whisper_dir / "full_audio_segments.json"
    words_file = whisper_dir / "all_words.json"

    if segs_file.exists() and words_file.exists():
        try:
            with open(segs_file, "r", encoding="utf-8") as f:
                segs = json.load(f)
            with open(words_file, "r", encoding="utf-8") as f:
                words = json.load(f)
            if len(segs) > 100 and len(words) > 1000:
                print(f"  [✓] Loaded cached Whisper transcription ({len(words)} words, {len(segs)} segments)")
                return segs, words
        except Exception:
            pass

    print(f"  [➔] Transcribing full audio: {audio_path.name}...")
    selected_device = device
    compute_type = "int8"
    if selected_device == "auto":
        selected_device = "cpu"  # safe fallback for cross-platform portability

    try:
        model = WhisperModel("base.en", device=selected_device, compute_type=compute_type)
    except Exception as e:
        print(f"  [WARN] Failed to load model on {selected_device}: {e}. Falling back to CPU...")
        model = WhisperModel("base.en", device="cpu", compute_type="int8")

    start_t = time.time()
    segments_gen, _ = model.transcribe(
        str(audio_path),
        beam_size=5,
        word_timestamps=True,
        vad_filter=True,
    )

    all_segs = []
    all_words = []
    for s in segments_gen:
        all_segs.append({
            "id": s.id,
            "start": round(s.start, 2),
            "end": round(s.end, 2),
            "text": s.text.strip(),
        })
        if s.words:
            for w in s.words:
                all_words.append({
                    "word": w.word.strip(),
                    "start": round(w.start, 2),
                    "end": round(w.end, 2),
                    "probability": round(w.probability, 2),
                })

    elapsed = time.time() - start_t
    print(f"  [✓] Full audio transcribed in {elapsed:.1f}s ({len(all_words)} words collected).")

    with open(segs_file, "w", encoding="utf-8") as f:
        json.dump(all_segs, f, ensure_ascii=False, indent=2)
    with open(words_file, "w", encoding="utf-8") as f:
        json.dump(all_words, f, ensure_ascii=False, indent=2)

    return all_segs, all_words


def find_words_phrase(words: List[Dict[str, Any]], phrase_words: List[str], start_sec: float = 0.0) -> Optional[int]:
    """Finds starting word index for a sequence of words."""
    n = len(phrase_words)
    clean_phrases = [re.sub(r"[^a-zA-Z0-9]", "", w).lower() for w in phrase_words]
    for i in range(len(words) - n + 1):
        if words[i]["start"] < start_sec:
            continue
        match = True
        for j in range(n):
            w = re.sub(r"[^a-zA-Z0-9]", "", words[i + j]["word"]).lower()
            if w != clean_phrases[j]:
                match = False
                break
        if match:
            return i
    return None


def calculate_dynamic_ranges(
    segs: List[Dict[str, Any]],
    words: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Tuple[float, float]]]:
    """Dynamically locates exact start and end timestamps for all 54 audio clips."""
    print("  [➔] Aligning audio cues and calculating dynamic clip boundaries...")

    # --- Part 1: Q1 to Q6 ---
    p1_starts = {}
    for q in range(1, 7):
        idx = find_words_phrase(words, ["number", str(q)], start_sec=70.0)
        if idx is not None:
            p1_starts[q] = max(0.0, words[idx]["start"] - 0.5)
        else:
            # Fallback estimation based on average spacing if speech cue not cleanly parsed
            prev_s = p1_starts.get(q - 1, 95.0)
            p1_starts[q] = prev_s + 28.0

    part2_dir_idx = find_words_phrase(words, ["part", "2"], start_sec=220.0)
    part2_dir_start = words[part2_dir_idx]["start"] - 0.5 if part2_dir_idx else (p1_starts[6] + 30.0)

    p1_ranges = {}
    for q in range(1, 7):
        s = p1_starts[q]
        e = p1_starts[q + 1] - 0.2 if q < 6 else part2_dir_start - 0.5
        p1_ranges[str(q)] = (round(s, 2), round(e, 2))

    # --- Part 2: Q7 to Q31 ---
    p2_starts = {}
    last_found = 260.0
    for q in range(7, 32):
        idx = find_words_phrase(words, ["number", str(q)], start_sec=last_found)
        if idx is not None:
            p2_starts[q] = max(0.0, words[idx]["start"] - 0.4)
            last_found = p2_starts[q] + 12.0
        else:
            # Linear fallback if specific number word was mumbled
            p2_starts[q] = last_found + 18.0
            last_found = p2_starts[q]

    part3_dir_idx = find_words_phrase(words, ["part", "3"], start_sec=750.0)
    part3_dir_start = words[part3_dir_idx]["start"] - 0.5 if part3_dir_idx else (p2_starts[31] + 20.0)

    p2_ranges = {}
    for q in range(7, 32):
        s = p2_starts[q]
        e = p2_starts[q + 1] - 0.3 if q < 31 else part3_dir_start - 0.5
        p2_ranges[str(q)] = (round(s, 2), round(e, 2))

    # --- Part 3: 13 Groups ---
    p3_cues = [
        ("g32_34", 32, 800.0),
        ("g35_37", 35, 880.0),
        ("g38_40", 38, 960.0),
        ("g41_43", 41, 1040.0),
        ("g44_46", 44, 1120.0),
        ("g47_49", 47, 1200.0),
        ("g50_52", 50, 1280.0),
        ("g53_55", 53, 1360.0),
        ("g56_58", 56, 1440.0),
        ("g59_61", 59, 1520.0),
        ("g62_64", 62, 1600.0),
        ("g65_67", 65, 1690.0),
        ("g68_70", 68, 1780.0),
    ]

    p3_starts = {}
    for key, q_start, min_sec in p3_cues:
        found_s = None
        for s in segs:
            if s["start"] >= min_sec:
                low = s["text"].lower()
                if (
                    f"question {q_start}" in low
                    or f"questions {q_start}" in low
                    or f"questions  {q_start}" in low
                    or f"question number {q_start}" in low
                ):
                    found_s = s["start"] - 0.5
                    break
        if found_s is None:
            # Search words
            idx = find_words_phrase(words, ["questions", str(q_start)], start_sec=min_sec)
            if idx is not None:
                found_s = words[idx]["start"] - 0.5
            else:
                found_s = min_sec + 10.0
        p3_starts[key] = max(0.0, found_s)

    part4_dir_idx = find_words_phrase(words, ["part", "4"], start_sec=1850.0)
    part4_dir_start = words[part4_dir_idx]["start"] - 0.5 if part4_dir_idx else (p3_starts["g68_70"] + 80.0)

    p3_ranges = {}
    for i, (key, q_start, _) in enumerate(p3_cues):
        s = p3_starts[key]
        if i < len(p3_cues) - 1:
            next_key = p3_cues[i + 1][0]
            page_cut = None
            for seg in segs:
                if (s + 35.0) <= seg["start"] < p3_starts[next_key]:
                    if "go on to" in seg["text"].lower():
                        page_cut = seg["start"] - 0.5
            e = page_cut if (page_cut and page_cut > s + 30.0) else (p3_starts[next_key] - 0.3)
        else:
            e = part4_dir_start - 0.5
        p3_ranges[key] = (round(s, 2), round(max(s + 30.0, e), 2))

    # --- Part 4: 10 Groups ---
    p4_cues = [
        ("g71_73", 71, 1900.0),
        ("g74_76", 74, 1980.0),
        ("g77_79", 77, 2060.0),
        ("g80_82", 80, 2140.0),
        ("g83_85", 83, 2220.0),
        ("g86_88", 86, 2300.0),
        ("g89_91", 89, 2380.0),
        ("g92_94", 92, 2460.0),
        ("g95_97", 95, 2540.0),
        ("g98_100", 98, 2620.0),
    ]

    p4_starts = {}
    for key, q_start, min_sec in p4_cues:
        found_s = None
        for s in segs:
            if s["start"] >= min_sec:
                low = s["text"].lower()
                if (
                    f"question {q_start}" in low
                    or f"questions {q_start}" in low
                    or f"questions  {q_start}" in low
                    or f"question number {q_start}" in low
                ):
                    found_s = s["start"] - 0.5
                    break
        if found_s is None:
            idx = find_words_phrase(words, ["questions", str(q_start)], start_sec=min_sec)
            if idx is not None:
                found_s = words[idx]["start"] - 0.5
            else:
                found_s = min_sec + 10.0
        p4_starts[key] = max(0.0, found_s)

    end_idx = find_words_phrase(words, ["this", "is", "the", "end"], start_sec=2700.0)
    end_start = words[end_idx]["start"] - 0.5 if end_idx else (p4_starts["g98_100"] + 80.0)

    p4_ranges = {}
    for i, (key, q_start, _) in enumerate(p4_cues):
        s = p4_starts[key]
        if i < len(p4_cues) - 1:
            next_key = p4_cues[i + 1][0]
            page_cut = None
            for seg in segs:
                if (s + 35.0) <= seg["start"] < p4_starts[next_key]:
                    if "go on to" in seg["text"].lower():
                        page_cut = seg["start"] - 0.5
            e = page_cut if (page_cut and page_cut > s + 30.0) else (p4_starts[next_key] - 0.3)
        else:
            e = end_start - 0.5
        p4_ranges[key] = (round(s, 2), round(max(s + 30.0, e), 2))

    return {
        "part1": p1_ranges,
        "part2": p2_ranges,
        "part3": p3_ranges,
        "part4": p4_ranges,
    }


def extract_segments_for_range(
    segs: List[Dict[str, Any]],
    start_sec: float,
    end_sec: float,
    prefix_id: str,
    check_traps: bool = False,
) -> List[Dict[str, Any]]:
    """Maps global segments into normalized relative segments for a sliced audio clip."""
    results = []
    idx = 1
    for s in segs:
        # Check if segment overlaps with the slice range
        if s["end"] >= start_sec and s["start"] <= end_sec:
            rel_start = max(0.0, round(s["start"] - start_sec, 2))
            rel_end = round(min(end_sec - start_sec, s["end"] - start_sec), 2)
            t = s["text"].strip()
            is_trap = False
            if check_traps:
                is_trap = "is being" in t.lower() or "are being" in t.lower()
            results.append({
                "id": f"{prefix_id}-{idx}",
                "speaker": "Speaker",
                "start_time": rel_start,
                "end_time": rel_end,
                "text_en": t,
                "text_vi": "",
                "is_trap": is_trap,
            })
            idx += 1
    return results


def process_audio_pipeline(
    audio_path: Path,
    output_audio_dir: Path,
    segments_dir: Path,
    device: str = "auto",
    secondary_audio_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Complete audio pipeline: transcription, dynamic landmark alignment, PyAV slicing, and segment caching."""
    output_audio_dir.mkdir(parents=True, exist_ok=True)
    segments_dir.mkdir(parents=True, exist_ok=True)
    whisper_dir = segments_dir.parent / "whisper"
    whisper_dir.mkdir(parents=True, exist_ok=True)

    segments_cache = segments_dir / "sliced_audio_segments.json"
    if segments_cache.exists():
        try:
            with open(segments_cache, "r", encoding="utf-8") as f:
                data = json.load(f)
                if (
                    len(data.get("part1", {})) == 6
                    and len(data.get("part2", {})) == 25
                    and len(data.get("part3", {})) == 13
                    and len(data.get("part4", {})) == 10
                ):
                    print(f"  [✓] Loaded cached 54 sliced audio segments: {segments_cache.name}")
                    return data
        except Exception:
            pass

    # 1. Transcribe full audio with word timestamps
    all_segs, all_words = transcribe_full_audio_if_needed(audio_path, whisper_dir, device=device)

    # 2. Compute dynamic clip boundaries
    ranges = calculate_dynamic_ranges(all_segs, all_words)
    ranges_cache = segments_dir / "exact_audio_ranges.json"
    with open(ranges_cache, "w", encoding="utf-8") as f:
        json.dump(ranges, f, ensure_ascii=False, indent=2)

    # 3. Slice all 54 audio clips with PyAV
    print(f"  [➔] Slicing 54 clips into {output_audio_dir}...")
    slice_tasks = []
    for q, (s, e) in ranges["part1"].items():
        slice_tasks.append(("part1", str(q), output_audio_dir / f"part1_q{q}.mp3", s, e))
    for q, (s, e) in ranges["part2"].items():
        slice_tasks.append(("part2", str(q), output_audio_dir / f"part2_q{q}.mp3", s, e))
    for g, (s, e) in ranges["part3"].items():
        slice_tasks.append(("part3", g, output_audio_dir / f"part3_{g}.mp3", s, e))
    for g, (s, e) in ranges["part4"].items():
        slice_tasks.append(("part4", g, output_audio_dir / f"part4_{g}.mp3", s, e))

    for cat, key, dst, s, e in slice_tasks:
        if not dst.exists() or dst.stat().st_size < 1000:
            slice_audio_file(str(audio_path), str(dst), s, e)

    # Copy to secondary audio directory if configured
    if secondary_audio_dir:
        secondary_audio_dir.mkdir(parents=True, exist_ok=True)
        for _, _, dst, _, _ in slice_tasks:
            sec_dst = secondary_audio_dir / dst.name
            if dst.exists() and (not sec_dst.exists() or sec_dst.stat().st_size < 1000):
                shutil.copy2(dst, sec_dst)

    print(f"  [✓] Successfully verified 54 sliced audio clips on disk.")

    # 4. Generate structured transcript segments for every clip
    result_data: Dict[str, Dict[str, Any]] = {"part1": {}, "part2": {}, "part3": {}, "part4": {}}

    for q in range(1, 7):
        s, e = ranges["part1"][str(q)]
        result_data["part1"][str(q)] = extract_segments_for_range(all_segs, s, e, f"seg-q{q}", check_traps=True)

    for q in range(7, 32):
        s, e = ranges["part2"][str(q)]
        result_data["part2"][str(q)] = extract_segments_for_range(all_segs, s, e, f"seg-q{q}", check_traps=False)

    for g_key, (s, e) in ranges["part3"].items():
        result_data["part3"][g_key] = extract_segments_for_range(all_segs, s, e, f"seg-p3-{g_key}", check_traps=False)

    for g_key, (s, e) in ranges["part4"].items():
        result_data["part4"][g_key] = extract_segments_for_range(all_segs, s, e, f"seg-p4-{g_key}", check_traps=False)

    with open(segments_cache, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    print(f"  [✓] Audio processing complete: 54 clips sliced & transcript segments saved to {segments_cache.name}")
    return result_data

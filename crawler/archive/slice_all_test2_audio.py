import os
import sys
import json
import time
import av
from pathlib import Path
from faster_whisper import WhisperModel

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def slice_audio(in_path, out_path, start_sec, end_sec):
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

def main():
    audio_path = "raw_data/TEST 2 - ETS 2023/Test 02 Audio.mp3"
    out_dir = Path("public/audio/test2")
    out_dir.mkdir(parents=True, exist_ok=True)

    segments_dir = Path("processed_data/TEST 2 - ETS 2023/intermediate/segments")
    segments_dir.mkdir(parents=True, exist_ok=True)

    p1_ranges = {
        1: (95.0, 123.5),
        2: (123.5, 148.0),
        3: (148.0, 180.6),
        4: (180.6, 206.0),
        5: (206.0, 233.2),
        6: (233.2, 264.0),
    }

    p2_ranges = {
        7:  (290.0, 311.0),
        8:  (311.0, 326.0),
        9:  (326.0, 348.0),
        10: (348.0, 370.0),
        11: (370.0, 392.0),
        12: (392.0, 407.0),
        13: (407.0, 430.0),
        14: (430.0, 448.0),
        15: (448.0, 468.0),
        16: (468.0, 489.0),
        17: (489.0, 514.0),
        18: (514.0, 534.0),
        19: (534.0, 550.0),
        20: (550.0, 571.0),
        21: (571.0, 591.0),
        22: (591.0, 613.0),
        23: (613.0, 632.0),
        24: (632.0, 656.0),
        25: (656.0, 680.0),
        26: (680.0, 701.0),
        27: (701.0, 723.0),
        28: (723.0, 744.0),
        29: (744.0, 766.0),
        30: (766.0, 788.0),
        31: (788.0, 808.0),
    }

    p3_ranges = {
        "g32_34": (828.0, 894.0),
        "g35_37": (894.0, 959.0),
        "g38_40": (959.0, 1045.0),
        "g41_43": (1045.0, 1118.0),
        "g44_46": (1118.0, 1218.0),
        "g47_49": (1218.0, 1296.0),
        "g50_52": (1296.0, 1355.0),
        "g53_55": (1355.0, 1447.0),
        "g56_58": (1447.0, 1525.0),
        "g59_61": (1525.0, 1607.0),
        "g62_64": (1607.0, 1698.0),
        "g65_67": (1698.0, 1783.0),
        "g68_70": (1783.0, 1873.0),
    }

    p4_ranges = {
        "g71_73": (1900.0, 1982.0),
        "g74_76": (1982.0, 2065.0),
        "g77_79": (2065.0, 2126.0),
        "g80_82": (2126.0, 2227.0),
        "g83_85": (2227.0, 2306.0),
        "g86_88": (2306.0, 2400.0),
        "g89_91": (2400.0, 2476.0),
        "g92_94": (2476.0, 2556.0),
        "g95_97": (2556.0, 2633.0),
        "g98_100": (2633.0, 2735.0),
    }

    # 1. Slice all audio files
    print("[1/2] Slicing audio files...")
    all_slices = []
    
    # Part 1
    for q, (s, e) in p1_ranges.items():
        dst = out_dir / f"part1_q{q}.mp3"
        all_slices.append(("p1", q, dst, s, e))
        
    # Part 2
    for q, (s, e) in p2_ranges.items():
        dst = out_dir / f"part2_q{q}.mp3"
        all_slices.append(("p2", q, dst, s, e))

    # Part 3
    for g, (s, e) in p3_ranges.items():
        dst = out_dir / f"part3_{g}.mp3"
        all_slices.append(("p3", g, dst, s, e))

    # Part 4
    for g, (s, e) in p4_ranges.items():
        dst = out_dir / f"part4_{g}.mp3"
        all_slices.append(("p4", g, dst, s, e))

    t0 = time.time()
    for cat, key, dst, s, e in all_slices:
        if not dst.exists() or dst.stat().st_size < 1000:
            slice_audio(audio_path, str(dst), s, e)
    print(f"  [✓] All {len(all_slices)} audio clips sliced in {time.time()-t0:.1f}s.")

    # 2. Transcribe each slice using faster-whisper on CPU int8
    print("[2/2] Transcribing slices for precise segment timestamps with faster-whisper...")
    device = "cpu"
    compute_type = "int8"
    print(f"  [➔] Loading Whisper base.en ({device}, {compute_type})...")
    model = WhisperModel("base.en", device=device, compute_type=compute_type)

    sliced_segments_data = {
        "part1": {},
        "part2": {},
        "part3": {},
        "part4": {},
    }

    # Transcribe Part 1
    print("  [-] Transcribing Part 1 (Q1-Q6)...")
    for q in range(1, 7):
        clip = str(out_dir / f"part1_q{q}.mp3")
        segs_gen, _ = model.transcribe(clip, beam_size=5)
        raw = list(segs_gen)
        # Parse (A), (B), (C), (D)
        q_segs = []
        for s in raw:
            t = s.text.strip()
            is_trap = "is being" in t.lower() or "are being" in t.lower()
            q_segs.append({
                "id": f"seg-q{q}-{len(q_segs)+1}",
                "speaker": "Speaker",
                "start_time": round(s.start, 2),
                "end_time": round(s.end, 2),
                "text_en": t,
                "text_vi": "",
                "is_trap": is_trap,
            })
        sliced_segments_data["part1"][str(q)] = q_segs

    # Transcribe Part 2
    print("  [-] Transcribing Part 2 (Q7-Q31)...")
    for q in range(7, 32):
        clip = str(out_dir / f"part2_q{q}.mp3")
        segs_gen, _ = model.transcribe(clip, beam_size=5)
        raw = list(segs_gen)
        q_segs = []
        for s in raw:
            q_segs.append({
                "id": f"seg-q{q}-{len(q_segs)+1}",
                "speaker": "Speaker",
                "start_time": round(s.start, 2),
                "end_time": round(s.end, 2),
                "text_en": s.text.strip(),
                "text_vi": "",
                "is_trap": False,
            })
        sliced_segments_data["part2"][str(q)] = q_segs

    # Transcribe Part 3
    print("  [-] Transcribing Part 3 (13 groups)...")
    for g_key in p3_ranges.keys():
        clip = str(out_dir / f"part3_{g_key}.mp3")
        segs_gen, _ = model.transcribe(clip, beam_size=5)
        raw = list(segs_gen)
        g_segs = []
        for s in raw:
            t = s.text.strip()
            # filter out question reading if needed or keep full dialog
            g_segs.append({
                "id": f"seg-p3-{g_key}-{len(g_segs)+1}",
                "speaker": "Speaker",
                "start_time": round(s.start, 2),
                "end_time": round(s.end, 2),
                "text_en": t,
                "text_vi": "",
                "is_trap": False,
            })
        sliced_segments_data["part3"][g_key] = g_segs

    # Transcribe Part 4
    print("  [-] Transcribing Part 4 (10 groups)...")
    for g_key in p4_ranges.keys():
        clip = str(out_dir / f"part4_{g_key}.mp3")
        segs_gen, _ = model.transcribe(clip, beam_size=5)
        raw = list(segs_gen)
        g_segs = []
        for s in raw:
            t = s.text.strip()
            g_segs.append({
                "id": f"seg-p4-{g_key}-{len(g_segs)+1}",
                "speaker": "Speaker",
                "start_time": round(s.start, 2),
                "end_time": round(s.end, 2),
                "text_en": t,
                "text_vi": "",
                "is_trap": False,
            })
        sliced_segments_data["part4"][g_key] = g_segs

    # Save to JSON
    out_json = segments_dir / "sliced_audio_segments.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(sliced_segments_data, f, ensure_ascii=False, indent=2)

    print(f"\n[✓] Audio processing complete! Sliced and transcribed 54 clips into {out_dir}")
    print(f"  ➔ Saved segment metadata to {out_json}")

if __name__ == "__main__":
    import ctranslate2
    main()

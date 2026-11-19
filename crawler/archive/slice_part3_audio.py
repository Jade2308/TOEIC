import os
import sys
import json
import av

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

audio_path = "raw_data/TEST 1 - ETS 2023/AUDIO Test 01.mp3"
output_dir = "public/audio/test1"
os.makedirs(output_dir, exist_ok=True)

# Precise timestamp boundaries for 13 conversation groups
group_ranges = {
    "g32_34": (834.0, 912.0),
    "g35_37": (912.0, 983.5),
    "g38_40": (983.5, 1054.0),
    "g41_43": (1054.0, 1130.0),
    "g44_46": (1136.5, 1218.5),
    "g47_49": (1218.5, 1294.0),
    "g50_52": (1294.0, 1365.5),
    "g53_55": (1365.5, 1441.0),
    "g56_58": (1441.0, 1531.0),
    "g59_61": (1531.0, 1616.0),
    "g62_64": (1616.0, 1704.5),
    "g65_67": (1711.0, 1798.5),
    "g68_70": (1798.5, 1891.5),
}

print(f"Slicing 13 Part 3 audio files from {audio_path}...")

for g_key, (start_sec, end_sec) in group_ranges.items():
    out_file = os.path.join(output_dir, f"part3_{g_key}.mp3")
    print(f"[{g_key}] {start_sec:.1f}s -> {end_sec:.1f}s (dur {end_sec-start_sec:.1f}s) -> {out_file}...")

    in_container = av.open(audio_path)
    in_stream = in_container.streams.audio[0]

    out_container = av.open(out_file, mode="w")
    out_stream = out_container.add_stream("mp3", rate=in_stream.rate)
    out_stream.bit_rate = in_stream.bit_rate or 128000

    # Seek close to start
    seek_target = int(max(0, start_sec - 1.0) / in_stream.time_base)
    in_container.seek(seek_target, stream=in_stream)

    for frame in in_container.decode(in_stream):
        curr_time = float(frame.pts * in_stream.time_base)
        if curr_time < start_sec:
            continue
        if curr_time > end_sec:
            break
        frame.pts = None
        for packet in out_stream.encode(frame):
            out_container.mux(packet)

    for packet in out_stream.encode():
        out_container.mux(packet)

    out_container.close()
    in_container.close()
    size_kb = os.path.getsize(out_file) / 1024
    print(f"  [OK] Saved {out_file} ({size_kb:.1f} KB)")

print("\nAll 13 Part 3 audio files sliced successfully!")

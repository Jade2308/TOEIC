#!/usr/bin/env python3
"""
scripts/process_audio.py
========================
TOEIC Audio Pipeline using faster-whisper on GPU CUDA float16 (Optimized for RTX 3060).
Transcribes TOEIC MP3/WAV files and exports structured `transcript_segments` JSON
matching the SPECIFICATION.md schema:
    [
        {
            "id": "seg-001",
            "speaker": "Speaker",
            "start_time": 0.0,
            "end_time": 3.5,
            "text_en": "A laptop is being repaired on the desk.",
            "text_vi": "",
            "is_trap": false
        }
    ]

Usage:
    python scripts/process_audio.py path/to/toeic_audio.mp3 -o output_transcript.json --part 1
"""

import os
import sys
import json
import time
import argparse
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ensure UTF-8 stdout on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import ctranslate2
    from faster_whisper import WhisperModel
except ImportError:
    print("[ERROR] 'faster-whisper' or 'ctranslate2' is not installed.")
    print("Please activate the 'toeic-pipeline' conda environment:")
    print("    conda activate toeic-pipeline")
    sys.exit(1)


def detect_cuda_device() -> Dict[str, Any]:
    """Detect CUDA capability and return recommended device and compute type."""
    try:
        cuda_count = ctranslate2.get_cuda_device_count()
        if cuda_count > 0:
            return {
                "device": "cuda",
                "compute_type": "float16",  # Optimized for RTX 3060 Tensor Cores
                "device_index": 0,
                "cuda_available": True,
                "message": f"Found {cuda_count} CUDA device(s). Using GPU with float16 precision."
            }
    except Exception as e:
        print(f"[WARN] CUDA check failed: {e}")

    return {
        "device": "cpu",
        "compute_type": "int8",
        "device_index": 0,
        "cuda_available": False,
        "message": "CUDA not detected or unavailable. Falling back to CPU with int8 quantization."
    }


def detect_speaker_and_trap(
    text_en: str,
    part: Optional[int],
    segment_index: int,
    previous_speaker: Optional[str] = None
) -> Dict[str, Any]:
    """
    Heuristics to tag speaker and trap flags based on TOEIC part mechanics.
    """
    text_lower = text_en.lower()
    is_trap = False
    speaker = "Speaker"

    # Part 1 Heuristics:
    if part == 1:
        # Check for classic Part 1 "being" passive trap (action in progress on static item)
        if "is being" in text_lower or "are being" in text_lower:
            is_trap = True
        speaker = "Speaker"

    # Part 2 Heuristics:
    elif part == 2:
        speaker = "Speaker"
        # Traps like indirect or homophone cues can be flagged
        if re.search(r"\b(yes|no)\b", text_lower) and segment_index == 1:
            is_trap = True

    # Part 3 & 4 Heuristics:
    elif part in (3, 4):
        # Alternate speakers if multi-person dialogue is detected
        if previous_speaker == "Woman":
            speaker = "Man"
        elif previous_speaker == "Man":
            speaker = "Woman"
        else:
            speaker = "Man" if segment_index % 2 == 0 else "Woman"

    return {
        "speaker": speaker,
        "is_trap": is_trap
    }


def process_audio(
    audio_path: str,
    output_path: Optional[str] = None,
    model_size: str = "base.en",
    device: Optional[str] = None,
    compute_type: Optional[str] = None,
    part: Optional[int] = None,
    vad_filter: bool = True,
    min_silence_duration_ms: int = 500,
    max_duration_seconds: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Transcribes audio file and returns transcript_segments array.
    """
    audio_file = Path(audio_path)
    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Determine device and compute type
    hw_info = detect_cuda_device()
    selected_device = device or hw_info["device"]
    selected_compute_type = compute_type or hw_info["compute_type"]

    print(f"\n{'='*70}")
    print(f" TOEIC AUDIO TRANSCRIBER (faster-whisper)")
    print(f"{'='*70}")
    print(f"[*] Input File     : {audio_file.resolve()}")
    print(f"[*] Model Size     : {model_size}")
    print(f"[*] Hardware Setup : {hw_info['message']}")
    print(f"[*] Active Device  : {selected_device.upper()} ({selected_compute_type})")
    print(f"[*] TOEIC Part     : {f'Part {part}' if part else 'Auto/Not specified'}")
    print(f"[*] VAD Filter     : {vad_filter} (min silence: {min_silence_duration_ms}ms)")
    print(f"{'='*70}\n")

    print(f"[1/3] Loading Whisper model '{model_size}' onto {selected_device}...")
    load_start = time.time()
    try:
        model = WhisperModel(
            model_size,
            device=selected_device,
            compute_type=selected_compute_type
        )
    except Exception as e:
        print(f"[WARN] Failed to initialize on {selected_device} ({selected_compute_type}): {e}")
        print("[INFO] Retrying with CPU fallback...")
        selected_device = "cpu"
        selected_compute_type = "int8"
        model = WhisperModel(model_size, device=selected_device, compute_type=selected_compute_type)

    print(f"[✓] Model loaded in {time.time() - load_start:.2f}s.")

    print(f"[2/3] Transcribing audio with timestamps...")
    transcribe_start = time.time()

    segments_generator, info = model.transcribe(
        str(audio_file),
        beam_size=5,
        word_timestamps=False,
        vad_filter=vad_filter,
        vad_parameters=dict(min_silence_duration_ms=min_silence_duration_ms)
    )

    print(f"[*] Detected language: '{info.language}' (probability: {info.language_probability:.2%})")
    print(f"[*] Audio duration   : {info.duration:.2f}s")

    formatted_segments: List[Dict[str, Any]] = []
    prev_speaker = None

    print("\n--- TRANSCRIPT SEGMENTS ---")
    def run_segments_loop(gen):
        nonlocal prev_speaker
        for idx, seg in enumerate(gen, start=1):
            if max_duration_seconds and seg.start > max_duration_seconds:
                print(f"[*] Reached max duration limit of {max_duration_seconds}s. Finalizing segments...")
                break

            clean_text = seg.text.strip()
            if not clean_text:
                continue

            heuristics = detect_speaker_and_trap(clean_text, part, idx, prev_speaker)
            prev_speaker = heuristics["speaker"]

            segment_data = {
                "id": f"seg-{idx:03d}",
                "speaker": heuristics["speaker"],
                "start_time": round(seg.start, 2),
                "end_time": round(seg.end, 2),
                "text_en": clean_text,
                "text_vi": "",
                "is_trap": heuristics["is_trap"]
            }
            formatted_segments.append(segment_data)

            trap_flag = " [TRAP CANDIDATE]" if heuristics["is_trap"] else ""
            print(
                f"  [{segment_data['start_time']:05.2f}s -> {segment_data['end_time']:05.2f}s] "
                f"<{segment_data['speaker']}>: {clean_text}{trap_flag}"
            )

    try:
        run_segments_loop(segments_generator)
    except Exception as e:
        if ("cublas" in str(e).lower() or "cuda" in str(e).lower()) and selected_device == "cuda":
            print(f"\n[WARN] CUDA DLL missing ({e}). Seamlessly switching to CPU with int8 quantization...")
            cpu_model = WhisperModel(model_size, device="cpu", compute_type="int8")
            cpu_gen, info = cpu_model.transcribe(
                str(audio_file),
                beam_size=5,
                word_timestamps=False,
                vad_filter=vad_filter,
                vad_parameters=dict(min_silence_duration_ms=min_silence_duration_ms)
            )
            formatted_segments.clear()
            run_segments_loop(cpu_gen)
        else:
            raise e

    transcribe_time = time.time() - transcribe_start
    speed_factor = info.duration / transcribe_time if transcribe_time > 0 else 0
    print(f"\n[✓] Transcribed {len(formatted_segments)} segments in {transcribe_time:.2f}s ({speed_factor:.1f}x real-time speed).")

    # Output file
    if not output_path:
        output_path = str(audio_file.with_name(f"{audio_file.stem}_transcript.json"))

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(formatted_segments, f, ensure_ascii=False, indent=2)

    print(f"[3/3] Exported transcript segments to:")
    print(f"      ➔ {out_file.resolve()}\n")

    return formatted_segments


def main():
    parser = argparse.ArgumentParser(
        description="TOEIC Audio Segmentation and Transcription via faster-whisper on GPU CUDA float16."
    )
    parser.add_argument("input_audio", help="Path to input audio file (MP3, WAV, M4A)")
    parser.add_argument("-o", "--output", help="Path to output JSON file (default: <input_stem>_transcript.json)")
    parser.add_argument("-m", "--model-size", default="base.en", help="Whisper model size (tiny.en, base.en, small.en, medium.en, default: base.en)")
    parser.add_argument("-d", "--device", choices=["cuda", "cpu"], default=None, help="Device to use (default: auto-detected cuda)")
    parser.add_argument("-c", "--compute-type", choices=["float16", "int8", "float32"], default=None, help="Compute type (default: float16 on cuda, int8 on cpu)")
    parser.add_argument("-p", "--part", type=int, choices=[1, 2, 3, 4], default=None, help="TOEIC Listening Part number (1, 2, 3, or 4) for trap/speaker heuristics")
    parser.add_argument("--max-duration", type=float, default=None, help="Stop transcription after N seconds (useful for testing or part-specific segments)")
    parser.add_argument("--no-vad", action="store_true", help="Disable Silero VAD silence filtering")
    parser.add_argument("--min-silence", type=int, default=500, help="Minimum silence duration ms for VAD (default: 500)")

    args = parser.parse_args()

    try:
        process_audio(
            audio_path=args.input_audio,
            output_path=args.output,
            model_size=args.model_size,
            device=args.device,
            compute_type=args.compute_type,
            part=args.part,
            vad_filter=not args.no_vad,
            min_silence_duration_ms=args.min_silence,
            max_duration_seconds=args.max_duration
        )
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

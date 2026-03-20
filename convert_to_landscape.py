#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Барлық видеоларды portrait (9:16) форматқа конвертациялайтын скрипт.
Пайдалану: python3 convert_to_landscape.py

ffmpeg орнатылған болуы керек:
  macOS:  brew install ffmpeg
  Ubuntu: sudo apt install ffmpeg
"""

import os
import subprocess
import sys

INPUT_DIR  = "videos"           # бастапқы видеолар
OUTPUT_DIR = "videos_portrait" # нәтиже видеолар

TARGET_W = 1080
TARGET_H = 1920


def get_video_info(path):
    """ffprobe арқылы видео өлшемін алу."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0",
        path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None, None
    parts = result.stdout.strip().split(",")
    if len(parts) == 2:
        return int(parts[0]), int(parts[1])
    return None, None


def convert_to_landscape(input_path, output_path):
    """
    Видеоны 1080x1920 portrait форматқа конвертациялау.
    Portrait видеолар: жанына қара жолақ қосылады (pillarbox).
    Landscape видеолар: тек scale + crop жасалады.
    """
    w, h = get_video_info(input_path)
    if w is None:
        print(f"  ⚠️  Өлшемді анықтай алмады: {input_path}")
        return False

    print(f"  📐 Бастапқы: {w}x{h}", end=" → ")

    # scale= aspect ratio сақтай отырып max 1920x1080 қылып кішірейтеді
    # pad=  1920x1080 өлшемге жеткізеді, ортасына орналастырады (қара фон)
    vf = (
        f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=decrease,"
        f"pad={TARGET_W}:{TARGET_H}:(ow-iw)/2:(oh-ih)/2:black"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"1920x1080 ✅")
        return True
    else:
        print(f"ҚАТЕ ❌")
        print(f"  ffmpeg error: {result.stderr[-500:]}")
        return False


def main():
    # ffmpeg бар-жоғын тексеру
    check = subprocess.run(["ffmpeg", "-version"], capture_output=True)
    if check.returncode != 0:
        print("❌ ffmpeg табылмады. Алдымен орнатыңыз:")
        print("   macOS:  brew install ffmpeg")
        print("   Ubuntu: sudo apt install ffmpeg")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    video_extensions = (".mp4", ".mov", ".avi", ".mkv", ".m4v", ".MOV", ".MP4")
    files = [
        f for f in sorted(os.listdir(INPUT_DIR))
        if f.endswith(video_extensions)
    ]

    if not files:
        print(f"⚠️  \'{INPUT_DIR}\' папкасында видео табылмады.")
        sys.exit(0)

    print(f"🎬 Барлығы {len(files)} видео конвертацияланады → portrait 1080x1920 (9:16)\n")

    success = 0
    for i, fname in enumerate(files, 1):
        input_path  = os.path.join(INPUT_DIR, fname)
        output_path = os.path.join(OUTPUT_DIR, fname)
        print(f"[{i}/{len(files)}] {fname}")
        if convert_to_landscape(input_path, output_path):
            success += 1

    print(f"\n✅ Дайын: {success}/{len(files)} видео сәтті конвертацияланды.")
    print(f"📁 Нәтиже: ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    main()

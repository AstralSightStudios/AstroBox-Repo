#!/usr/bin/env python3
"""把「WebM 动画 + 黑白蒙版」合成为透明底 Animated WebP。

用法：
    python3 convert_webm_to_webp.py --input <webm目录> --mask-dir <蒙版目录> --output <输出目录> [--fps 60]

输入约定：
    - input 目录下有 <name>.webm（如 0.webm、1.webm …）
    - mask-dir 目录下有同名的 <name>.png 黑白蒙版（白色=前景，黑色=透明）
    - WebM 通常为 yuv420p（无 alpha 通道），尺寸为蒙版尺寸的偶数对齐版

输出：
    - output 目录下生成同名 <name>.webp（透明底、无限循环动画）
"""
import argparse
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image


def read_webm_fps(webm: str) -> int:
    try:
        out = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=r_frame_rate",
                "-of", "default=noprint_wrappers=1:nokey=1",
                webm,
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        num, _, den = out.partition("/")
        fps = float(num) / float(den or 1)
        return max(1, round(fps))
    except Exception:
        return 60


def convert_webm_to_webp(webm: str, mask: str, out: str, fps: int) -> None:
    src_fps = read_webm_fps(webm)
    out_fps = min(fps or src_fps, src_fps)
    step = max(1, round(src_fps / out_fps))
    duration = max(1, round(1000 / (src_fps / step)))

    with tempfile.TemporaryDirectory() as td:
        subprocess.run(
            ["ffmpeg", "-y", "-i", webm, f"{td}/f_%05d.png"],
            check=True,
            capture_output=True,
        )
        frame_paths = sorted(f for f in os.listdir(td) if f.startswith("f_"))
        if not frame_paths:
            raise RuntimeError(f"未能从 {webm} 抽取任何帧")

        # 蒙版（白=不透明）→ alpha
        mask_im = Image.open(mask).convert("L")
        mask_w, mask_h = mask_im.size
        alpha = np.asarray(mask_im, dtype=np.float64) / 255.0

        rgba_frames = []
        for name in frame_paths[::step]:
            im = Image.open(os.path.join(td, name)).convert("RGB")
            if im.size != (mask_w, mask_h):
                im = im.resize((mask_w, mask_h), Image.LANCZOS)
            rgb = np.asarray(im, dtype=np.float64)
            # 预乘 alpha，半透明边缘颜色才正确
            premul = (rgb * alpha[..., None]).astype(np.uint8)
            rgba = np.dstack([premul, (alpha * 255).astype(np.uint8)])
            rgba_frames.append(Image.fromarray(rgba, "RGBA"))

        rgba_frames[0].save(
            out,
            save_all=True,
            append_images=rgba_frames[1:],
            duration=duration,
            loop=0,
            quality=90,
            method=4,
        )
        print(
            f"  {os.path.basename(webm)}: {src_fps}fps→{(src_fps + step - 1) // step}fps, "
            f"{len(rgba_frames)}帧, {os.path.getsize(out)} bytes"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="WebM 所在目录")
    parser.add_argument("--mask-dir", required=True, help="黑白蒙版 PNG 所在目录")
    parser.add_argument("--output", required=True, help="WebP 输出目录")
    parser.add_argument("--fps", type=int, default=60, help="输出帧率（不超过源帧率，默认 60）")
    args = parser.parse_args()

    webms = sorted(
        f for f in os.listdir(args.input)
        if f.lower().endswith(".webm") and os.path.isfile(os.path.join(args.input, f))
    )
    if not webms:
        print("未找到 .webm 文件")
        return 1

    os.makedirs(args.output, exist_ok=True)
    for webm in webms:
        name = os.path.splitext(webm)[0]
        mask = os.path.join(args.mask_dir, f"{name}.png")
        if not os.path.isfile(mask):
            print(f"[跳过] {name}: 缺少蒙版 {mask}")
            continue
        try:
            convert_webm_to_webp(
                os.path.join(args.input, webm),
                mask,
                os.path.join(args.output, f"{name}.webp"),
                args.fps,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[失败] {name}: {exc}")
    print("完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())

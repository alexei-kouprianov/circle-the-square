#!/usr/bin/env python3

import cv2
import numpy as np
import os
import sys
import argparse


DEFAULT_FADE_WIDTH_RATIO = 0.06
DEFAULT_RADIUS_REDUCTION = 100


def detect_circle(img):
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.GaussianBlur(gray, (9, 9), 1.5)

    circles = cv2.HoughCircles(
        gray_blur,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=min(h, w) // 2,
        param1=100,
        param2=30,
        minRadius=int(min(h, w) * 0.3),
        maxRadius=int(min(h, w) * 0.48),
    )

    if circles is None:
        return None

    x, y, r = circles[0][0]
    return int(x), int(y), int(r)


def apply_circle(img, x, y, r, fade_width_ratio):
    h, w = img.shape[:2]

    yy, xx = np.ogrid[:h, :w]
    dist = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)

    fade_width = max(1, int(r * fade_width_ratio))

    mask = np.ones((h, w), dtype=np.float32)
    mask[dist >= r] = 0.0

    fade_zone = (dist >= r - fade_width) & (dist < r)
    mask[fade_zone] = (r - dist[fade_zone]) / fade_width

    white_bg = np.full_like(img, 255)
    mask_3c = cv2.merge([mask, mask, mask])

    return (img * mask_3c + white_bg * (1 - mask_3c)).astype(np.uint8)


def main():
    parser = argparse.ArgumentParser(
        description="Bleach microscope images outside the circular field of view."
    )

    parser.add_argument(
        "-f", "--fade",
        type=float,
        default=DEFAULT_FADE_WIDTH_RATIO,
        help=(
            "Fade width ratio relative to circle radius "
            "(default: 0.06; typical: 0.03 sharp, 0.05–0.07 natural)"
        ),
    )

    parser.add_argument(
        "-r", "--reduce-radius",
        type=int,
        default=DEFAULT_RADIUS_REDUCTION,
        help=(
            "Radius reduction in pixels applied after median radius detection "
            "(default: 100)"
        ),
    )

    parser.add_argument(
        "images",
        nargs="+",
        help="Input image files (globs expanded by the shell)",
    )

    args = parser.parse_args()

    if not (0.0 < args.fade < 0.5):
        parser.error("Fade width ratio must be between 0 and 0.5")

    if args.reduce_radius < 0:
        parser.error("Radius reduction must be >= 0")

    image_paths = args.images

    base_dir = os.path.dirname(os.path.abspath(image_paths[0]))
    out_dir = os.path.join(base_dir, "bleached")
    os.makedirs(out_dir, exist_ok=True)

    log_path = os.path.join(out_dir, "session.log")

    print(f"Fade width ratio: {args.fade}")
    print(f"Radius reduction: {args.reduce_radius} px")
    print(f"Output directory: {out_dir}")

    detected = []
    failed = []

    # ---------- Pass 1: detect circles ----------
    for path in image_paths:
        img = cv2.imread(path)
        if img is None:
            failed.append(path)
            continue

        circle = detect_circle(img)
        if circle is None:
            failed.append(path)
        else:
            detected.append(circle)

    if not detected:
        print("ERROR: No circles detected in any image.")
        sys.exit(1)

    xs, ys, rs = zip(*detected)
    mx = int(np.median(xs))
    my = int(np.median(ys))
    mr = int(np.median(rs))

    # Apply radius reduction
    mr_reduced = max(1, mr - args.reduce_radius)

    print(
        f"Median circle: x={mx}, y={my}, r={mr} → reduced r={mr_reduced}"
    )
    print(f"Detected in {len(detected)} / {len(image_paths)} images")

    # ---------- Pass 2: apply ----------
    for path in image_paths:
        img = cv2.imread(path)
        if img is None:
            continue

        result = apply_circle(img, mx, my, mr_reduced, args.fade)
        out_path = os.path.join(out_dir, os.path.basename(path))
        cv2.imwrite(out_path, result)

    # ---------- Logging ----------
    if failed:
        with open(log_path, "w") as f:
            for p in failed:
                f.write(p + "\n")

        print(f"Circle detection failed for {len(failed)} images.")
        print(f"See log: {log_path}")
    else:
        print("Circle detected successfully in all images.")


if __name__ == "__main__":
    main()

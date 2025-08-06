#!/usr/bin/env python3

from PIL import Image
from pathlib import Path

# Pfad zum Zielverzeichnis (relativ oder absolut)
target_dir = Path("public")
quality = 80

print(f"🔍 Find images in: {target_dir.resolve()}")


for img_path in target_dir.rglob("*.[jJ][pP][eE]?[gG]"):
    webp_path = img_path.with_suffix(".webp")

    if webp_path.exists():
        print(f"⚠️  Skipping (already exists): {webp_path}")
        continue

    try:
        with Image.open(img_path) as img:
            img.save(webp_path, "webp", quality=quality)
            print(f"✅ Converted: {img_path} → {webp_path}")
    except Exception as e:
        print(f"❌ Error processing {img_path}: {e}")

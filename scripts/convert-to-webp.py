#!/usr/bin/env python3

from PIL import Image
from pathlib import Path

# Pfad zum Zielverzeichnis (relativ oder absolut)
target_dir = Path("public")
quality = 80
valid_extensions = (".jpg", ".jpeg", ".png")

print(f"🔍 Searching for images in: {target_dir.resolve()}")

# Alle Dateien rekursiv durchsuchen
image_files = [
    p for p in target_dir.rglob("*")
    if p.is_file() and p.suffix.lower() in valid_extensions
]



if not image_files:
    print("⚠️  No matching images found.")
else:
    for img_path in image_files:
        print(f"📷 Processing: {img_path}")
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

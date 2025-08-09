#!/usr/bin/env python3

from PIL import Image
from pathlib import Path

# Pfad zum Zielverzeichnis (relativ oder absolut)
target_dir = Path("public")
quality = 80
valid_extensions = (".jpg", ".jpeg", ".png")
sizes = [320, 640, 960, 1280]  # gewünschte Breiten

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

        # Resized WebP erstellen
        for size in sizes:
            webp_resized = img_path.with_name(f"{img_path.stem}-{size}w.webp")
            if webp_resized.exists():
                print(f"⚠️  Skipping (already exists): {webp_resized}")
                continue

            try:
                with Image.open(img_path) as img:
                    width_percent = size / float(img.width)
                    height = int((float(img.height) * float(width_percent)))
                    img_resized = img.resize((size, height), Image.LANCZOS)
                    img_resized.save(webp_resized, "webp", quality=quality)
                    print(f"✅ Created resized WebP: {webp_resized}")
            except Exception as e:
                print(f"❌ Error processing {img_path}: {e}")

        # delete original file if it was converted
        if img_path.exists():
            try:
                img_path.unlink()
                print(f"🗑️  Deleted original file: {img_path}")
            except Exception as e:
                print(f"❌ Error deleting {img_path}: {e}")

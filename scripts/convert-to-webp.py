#!/usr/bin/env python3

from PIL import Image
from pathlib import Path

# Global settings
target_dir = Path("public")  # Path to target directory (relative or absolute)
quality = 80
valid_extensions = (".jpg", ".jpeg", ".png")
sizes = [320, 640, 960, 1280]  # Desired widths


OVERWRITE = False

print(f"🔍 Searching for images in: {target_dir.resolve()}")
print(f"⚙️  Overwrite mode: {'ON' if OVERWRITE else 'OFF'}")

# Search all files recursively
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

        # Base WebP conversion
        if webp_path.exists() and not OVERWRITE:
            print(f"⚠️  Skipping (already exists, overwrite OFF): {webp_path}")
        else:
            try:
                with Image.open(img_path) as img:
                    img.save(webp_path, "webp", quality=quality)
                    if webp_path.exists() and OVERWRITE:
                        print(f"♻️  Overwrote existing WebP: {webp_path}")
                    else:
                        print(f"✅ Converted: {img_path} → {webp_path}")
            except Exception as e:
                print(f"❌ Error processing {img_path}: {e}")

        # Resized WebP variants
        for size in sizes:
            webp_resized = img_path.with_name(f"{img_path.stem}-{size}w.webp")

            if webp_resized.exists() and not OVERWRITE:
                print(f"⚠️  Skipping resized (already exists, overwrite OFF): {webp_resized}")
                continue

            try:
                with Image.open(img_path) as img:
                    width_percent = size / float(img.width)
                    height = int(float(img.height) * width_percent)
                    img_resized = img.resize((size, height), Image.LANCZOS)
                    img_resized.save(webp_resized, "webp", quality=quality)

                    if webp_resized.exists() and OVERWRITE:
                        print(f"♻️  Overwrote resized WebP: {webp_resized}")
                    else:
                        print(f"✅ Created resized WebP: {webp_resized}")
            except Exception as e:
                print(f"❌ Error processing resized variant for {img_path}: {e}")

        # delete original file if it was converted
        # excluded_images = ["favicon", "icon", "logo", "thumbnail", "manifest"]
        # if img_path.exists() and not any(excluded in img_path.name for excluded in excluded_images):
        #     try:
        #         img_path.unlink()
        #         print(f"🗑️  Deleted original file: {img_path}")
        #     except Exception as e:
        #         print(f"❌ Error deleting {img_path}: {e}")
    print("🎉 Conversion process completed.")
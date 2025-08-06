#!/usr/bin/env python3

import os
import json
from PIL import Image
from pathlib import Path
import google.generativeai as genai

# 📁 Einstellungen
target_dir = Path("public")
quality = 80
output_json = "image_metadata.json"
valid_extensions = (".jpg", ".jpeg", ".png")

# 🔑 Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")


def load_processed():
    if not Path(output_json).exists():
        return []
    with open(output_json, "r", encoding="utf-8") as f:
        return json.load(f)


def save_processed(data):
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_description(image_path):
    img = Image.open(image_path)

    prompt = (
        "Du bist ein SEO-Experte. Analysiere das Bild und gib Folgendes zurück:\n"
        "1. Einen neuen, SEO-freundlichen Dateinamen (nur Kleinbuchstaben, keine Umlaute, Bindestriche, keine Endung).\n"
        "2. Einen barrierefreien Alt-Text.\n"
        "Format:\nDateiname: <...>\nAlt-Text: <...>"
    )

    response = model.generate_content(
        [prompt, img],
        generation_config={"temperature": 0.4}
    )

    return response.text


def parse_response(text):
    lines = text.strip().splitlines()
    filename = None
    alt_text = None
    for line in lines:
        if line.lower().startswith("dateiname:"):
            filename = line.split(":", 1)[1].strip()
        elif line.lower().startswith("alt-text:"):
            alt_text = line.split(":", 1)[1].strip()
    return filename, alt_text


def main():
    print(f"🔍 Searching for images in: {target_dir.resolve()}")
    image_files = [
        p for p in target_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in valid_extensions
    ]

    if not image_files:
        print("⚠️  No matching images found.")
        return

    processed = load_processed()
    already_done = {entry["original"] for entry in processed}
    new_entries = []

    for img_path in image_files:
        rel_path = str(img_path.relative_to(target_dir))

        if rel_path in already_done:
            print(f"⏭️  Skipping metadata (already processed): {rel_path}")
        else:
            try:
                print(f"🧠 Generating metadata for: {rel_path}")
                result = generate_description(img_path)
                filename, alt = parse_response(result)

                if filename and alt:
                    new_entries.append({
                        "original": rel_path,
                        "filename": filename + img_path.suffix.lower(),
                        "alt": alt
                    })
                    processed.append(new_entries[-1])
                    print(f"✅ Metadata generated: {filename}")
                else:
                    print(f"⚠️  Failed to parse Gemini response for {rel_path}")
            except Exception as e:
                print(f"❌ Error generating metadata for {rel_path}: {e}")

        # WebP-Konvertierung
        webp_path = img_path.with_suffix(".webp")
        if webp_path.exists():
            print(f"⚠️  Skipping WebP (already exists): {webp_path}")
            continue

        try:
            with Image.open(img_path) as img:
                img.save(webp_path, "webp", quality=quality)
                print(f"🖼️  Converted to WebP: {webp_path}")
        except Exception as e:
            print(f"❌ Error converting {img_path}: {e}")

    save_processed(processed)
    print(f"\n💾 {len(new_entries)} new entries saved to {output_json}")


if __name__ == "__main__":
    main()

import os
import json
from PIL import Image
from pathlib import Path

# New Google GenAI SDK
from google import genai
from google.genai import types

# 📁 Settings
target_dir = Path(r"D:\projects\islandhunde-ostsee\static\images\wuerfe\a\week4")
quality = 80
output_json = "image_metadata.json"
valid_extensions = (".jpg", ".jpeg", ".png")

# 🔑 Gemini / Google AI client (uses GEMINI_API_KEY or GOOGLE_API_KEY)
client = genai.Client()
MODEL_ID = "gemini-2.5-flash"  # current multimodal alias
CAPTION_TEMPERATURE = 0.9
DESC_TEMPERATURE = 0.4


def load_metadata():
    if not Path(output_json).exists():
        return {}
    with open(output_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        return {entry["original"]: entry for entry in data}


def save_metadata(metadata_dict):
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(list(metadata_dict.values()), f, indent=2, ensure_ascii=False)


def _read_image_as_bytes(image_path: Path):
    # Validate it's an image
    with Image.open(image_path) as _:
        pass
    mime = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
    }.get(image_path.suffix.lower(), "image/jpeg")
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    return image_bytes, mime


def generate_captions(image_path: Path):
    # (Keep your original German prompt exactly)
    prompt = (
        "Stelle dir vor, du schreibst für die Webseite einer kleinen, liebevollen Islandhundezucht. "
        "Auf dem Bild ist ein Islandhund (oder mehrere) aus unserer Zucht zu sehen. "
        "Formuliere 4 kurze, natürliche Bildunterschriften, die authentisch wirken, nicht werblich sind, "
        "und zu einer echten Familienzucht passen. "
        "Kein Marketing-Sprech, keine Emojis, keine übertriebene Sprache. "
        "Die Bildunterschriften sollen ruhig, bodenständig und bildbeschreibend sein.\n"
        "Gib nur die vier Bildunterschriften in einer nummerierten Liste zurück."
    )

    image_bytes, mime = _read_image_as_bytes(image_path)

    resp = client.models.generate_content(
        model=MODEL_ID,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime),
            prompt,
        ],
        config=types.GenerateContentConfig(temperature=CAPTION_TEMPERATURE),
    )
    print(f"📝 Gemini response: {getattr(resp, 'text', '')}")
    return getattr(resp, "text", "") or ""


def parse_captions(text: str):
    lines = text.strip().splitlines()
    captions = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line[0].isdigit():
            parts = line.split(".", 1)
            if len(parts) == 2:
                caption = parts[1].strip()
                if caption:
                    captions.append(caption)
    return captions


def generate_description(image_path: Path):
    # (Keep your original German prompt exactly)
    prompt = (
        "Du bist ein SEO-Experte. Gehe davon aus, dass alle Hunde auf den Bildern Islandhunde unserer Zucht sind. Analysiere das Bild und gib Folgendes zurück:\n"
        "1. Einen neuen, SEO-freundlichen Dateinamen (nur Kleinbuchstaben, keine Umlaute, Bindestriche, keine Endung).\n"
        "2. Einen barrierefreien Alt-Text.\n"
        "Format:\nDateiname: <...>\nAlt-Text: <...>"
    )

    image_bytes, mime = _read_image_as_bytes(image_path)

    resp = client.models.generate_content(
        model=MODEL_ID,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime),
            prompt,
        ],
        config=types.GenerateContentConfig(temperature=DESC_TEMPERATURE),
    )

    return getattr(resp, "text", "") or ""


def parse_response(text: str):
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

    metadata = load_metadata()
    updated = 0

    for img_path in image_files:
        rel_path = str(img_path.relative_to(target_dir))
        entry = metadata.get(rel_path, {"original": rel_path})

        try:
            # Add image dimensions if missing
            with Image.open(img_path) as img:
                width, height = img.size
            if "width" not in entry or "height" not in entry:
                entry["width"] = width
                entry["height"] = height
                print(f"➕ Added dimensions: {rel_path}")
                updated += 1
        except Exception as e:
            print(f"❌ Failed to read image size for {rel_path}: {e}")
            continue

        # Generate filename + alt only if needed
        if "filename" not in entry or "alt" not in entry:
            try:
                print(f"🧠 Generating metadata: {rel_path}")
                result = generate_description(img_path)
                filename, alt = parse_response(result)
                if filename and alt:
                    entry["filename"] = filename + img_path.suffix.lower()
                    entry["alt"] = alt
                    print(f"✅ Metadata generated: {entry['filename']}")
                    updated += 1
                else:
                    print(f"⚠️  Gemini response could not be parsed: {rel_path}")
            except Exception as e:
                print(f"❌ Gemini error for {rel_path}: {e}")
                continue

        # Generate captions if missing
        if "captions" not in entry:
            try:
                excluded_images = ["favicon", "icon", "logo", "thumbnail", "manifest"]
                if any(excluded in rel_path.lower() for excluded in excluded_images):
                    print(f"⏭️  Skipping excluded image: {rel_path}")
                    continue

                with Image.open(img_path) as img:
                    width, height = img.size

                # Skip very small assets (likely icons)
                if width < 300 or height < 300:
                    print(f"⏭️  Skipping small image: {rel_path}")
                    continue

                print(f"🧠 Generating captions: {rel_path}")
                captions_raw = generate_captions(img_path)
                captions = parse_captions(captions_raw)
                if captions:
                    entry["captions"] = captions
                    print(f"✅ {len(captions)} captions added")
                    updated += 1
                else:
                    print(f"⚠️  Gemini caption response could not be parsed: {rel_path}")
            except Exception as e:
                print(f"❌ Gemini caption error for {rel_path}: {e}")

        # Create WebP if missing
        webp_path = img_path.with_suffix(".webp")
        if not webp_path.exists():
            try:
                with Image.open(img_path) as img:
                    img.save(webp_path, "webp", quality=quality)
                    print(f"🖼️  Converted to WebP: {webp_path}")
            except Exception as e:
                print(f"❌ WebP conversion failed for {rel_path}: {e}")

        # Save / update entry
        metadata[rel_path] = entry

    save_metadata(metadata)
    print(f"\n💾 {updated} entries updated or added in {output_json}")


if __name__ == "__main__":
    main()

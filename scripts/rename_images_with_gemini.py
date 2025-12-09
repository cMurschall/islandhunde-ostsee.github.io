import os
from pathlib import Path
from PIL import Image
from google import genai
from google.genai import types

# ── Config ────────────────────────────────────────────────────────────────────
TARGET_DIR = Path(r"D:\projects\islandhunde-ostsee\static\images\wuerfe\a\week8")
VALID_EXTS = (".jpg", ".jpeg", ".png")
MODEL_ID = "gemini-2.5-flash"  # multimodal, current alias
TEMPERATURE = 0.3

client = genai.Client()  # picks up GEMINI_API_KEY or GOOGLE_API_KEY


def slugify_basename(text: str) -> str:
    """
    Convert to SEO-safe slug:
      - lowercase
      - replace German umlauts/ß
      - keep alnum and hyphens only
      - collapse duplicate hyphens
    """
    mapping = {
        "ä": "ae", "ö": "oe", "ü": "ue",
        "Ä": "ae", "Ö": "oe", "Ü": "ue",
        "ß": "ss",
    }
    for k, v in mapping.items():
        text = text.replace(k, v)
    text = text.lower()
    # Replace spaces/underscores with hyphen
    text = text.replace(" ", "-").replace("_", "-")
    # Remove everything not a-z0-9 or hyphen
    import re
    text = re.sub(r"[^a-z0-9-]", "", text)
    # Collapse multiple hyphens
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "islandhund"


def generate_new_filename(image_path: Path) -> str:
    # Load bytes; Pillow open just to validate it's an image
    with Image.open(image_path) as _:
        pass
    mime = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
    }[image_path.suffix.lower()]

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    prompt = (
        "You are an SEO expert. Return a concise, SEO-friendly file name for this "
        "photo of one or more Icelandic Sheepdogs (\"Islandhund\" in German) or Icelandic puppies. "
        "Rules: lowercase only, no umlauts or special characters, use hyphens instead of spaces. "
        "Return only the new base name without file extension and without any extra text."
    )

    resp = client.models.generate_content(
        model=MODEL_ID,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime),
            prompt,
        ],
        config=types.GenerateContentConfig(temperature=TEMPERATURE),
    )

    suggestion = (resp.text or "").strip()
    return slugify_basename(suggestion)


def rename_with_gemini():
    print(f"📁 Scanning: {TARGET_DIR.resolve()}")
    files = [p for p in TARGET_DIR.iterdir() if p.is_file() and p.suffix.lower() in VALID_EXTS]

    if not files:
        print("⚠️  No matching image files found.")
        return

    for img_path in files:
        try:
            print(f"🔍 Processing: {img_path}")
            new_base = generate_new_filename(img_path)
            if not new_base:
                print("⚠️  No valid suggestion received.")
                continue

            new_path = img_path.with_name(new_base + img_path.suffix.lower())

            if new_path.exists():
                print(f"⚠️  Target exists: {new_path.name} -> applying increment")
                base, ext = new_path.stem, new_path.suffix
                counter = 1
                while new_path.exists() and counter <= 100:
                    new_path = img_path.with_name(f"{base}-{counter}{ext}")
                    counter += 1
                if new_path.exists():
                    print("❗️ Too many conflicts, skipping.")
                    continue

            print(f"✅ New name: {new_path.name}")
            img_path.rename(new_path)
            print(f"✅ Renamed to: {new_path.name}")

        except Exception as e:
            print(f"❌ Error on {img_path.name}: {e}")



if __name__ == "__main__":
    rename_with_gemini()
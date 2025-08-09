import os
from pathlib import Path
from PIL import Image
import google.generativeai as genai

# 📁 Konfiguration
target_dir = Path("D:\\projects\\islandhunde-ostsee\\static\\images\\unndis")  # Nur dieser Ordner, nicht rekursiv
valid_extensions = (".jpg", ".jpeg", ".png")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")


def generate_new_filename(image_path):
    img = Image.open(image_path)

    prompt = (
        "Du bist ein SEO-Experte. Gib einen neuen, SEO-freundlichen Dateinamen für dieses Bild eines oder mehreren Islandhunde zurück. "
        "Der Name soll nur aus Kleinbuchstaben bestehen, keine Umlaute oder Sonderzeichen enthalten und mit Bindestrichen statt Leerzeichen arbeiten. "
        "Gib **nur** den neuen Dateinamen zurück, **ohne** Dateiendung und ohne zusätzliche Erklärung."
    )

    response = model.generate_content([prompt, img], generation_config={"temperature": 0.3})
    return response.text.strip()


def rename_with_gemini():
    print(f"📁 Durchsuche Ordner: {target_dir.resolve()}")
    files = [p for p in target_dir.iterdir() if p.suffix.lower() in valid_extensions and p.is_file()]

    if not files:
        print("⚠️  Keine passenden Bilddateien gefunden.")
        return

    for img_path in files:
        try:
            print(f"🔍 Bearbeite: {img_path}")

            new_name = generate_new_filename(img_path)
            if not new_name:
                print("⚠️  Kein gültiger Vorschlag erhalten.")
                continue

            new_path = img_path.with_name(new_name + img_path.suffix.lower())

            if new_path.exists():
                print(f"⚠️  Zieldatei existiert bereits: {new_path.name}")
                # incremental renaming
                base, ext = new_path.stem, new_path.suffix
                counter = 1
                while new_path.exists():
                    new_path = img_path.with_name(f"{base}-{counter}{ext}")
                    counter += 1
                    if counter > 100:
                        print("❗️ Zu viele Konflikte, Abbruch.")
                        break
                continue
            print(f"✅ Neuer Name: {new_name + img_path.suffix.lower()}")


            img_path.rename(new_path)
            print(f"✅ Umbenannt in: {new_path.name}")

        except Exception as e:
            print(f"❌ Fehler bei {img_path.name}: {e}")

def rename_hund_to_islandhund():
    print(f"🔁 Ersetze 'hund' durch 'islandhund' in Dateinamen unter: {target_dir.resolve()}")
    files = [p for p in target_dir.iterdir() if p.suffix.lower() in valid_extensions and p.is_file()]

    for img_path in files:
        if "hund" in img_path.name.lower():
            new_name = img_path.name.lower().replace("hund", "islandhund")
            new_path = img_path.with_name(new_name)

            if new_path.exists():
                print(f"⚠️  Ziel existiert bereits: {new_path.name} – übersprungen.")
                continue

            img_path.rename(new_path)
            print(f"✅ Umbenannt: {img_path.name} → {new_path.name}")


def rename_border_collie_to_islandhund():
    print(f"🔁 Ersetze 'border-collie' durch 'islandhund' in Dateinamen unter: {target_dir.resolve()}")
    files = [p for p in target_dir.iterdir() if p.suffix.lower() in valid_extensions and p.is_file()]

    for img_path in files:
        if "border-collie" in img_path.name.lower():
            new_name = img_path.name.lower().replace("border-collie", "islandhund")
            new_path = img_path.with_name(new_name)

            if new_path.exists():
                print(f"⚠️  Ziel existiert bereits: {new_path.name} – übersprungen.")
                continue

            img_path.rename(new_path)
            print(f"✅ Umbenannt: {img_path.name} → {new_path.name}")


if __name__ == "__main__":
    rename_with_gemini()
    # rename_hund_to_islandhund()
    #rename_border_collie_to_islandhund()

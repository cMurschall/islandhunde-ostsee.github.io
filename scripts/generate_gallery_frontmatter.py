import json
from pathlib import Path
from collections import defaultdict
import yaml

# 📁 Einstellungen
metadata_file = "image_metadata.json"
base_url = "/images/"
output_dir = Path("gallery_output")

def load_metadata():
    with open(metadata_file, "r", encoding="utf-8") as f:
        return json.load(f)

def group_by_first_folder(metadata):
    grouped = defaultdict(list)
    for entry in metadata:
        rel_path = Path(entry["original"].replace("\\", "/"))
        parts = rel_path.parts

        if len(parts) > 1:
            folder = parts[1] if parts[0] == "images" else parts[0]
        else:
            folder = "root"

        grouped[folder].append((rel_path, entry))

    return grouped

def build_gallery_entry(rel_path, entry):
    return {
        "src": "/" + str(rel_path).replace("\\", "/"),
        "alt": entry.get("alt", ""),
        "caption": entry.get("captions", [""])[0],
        "width": entry.get("width", 0),
        "height": entry.get("height", 0)
    }

def generate_gallery_files():
    metadata = load_metadata()
    grouped = group_by_first_folder(metadata)

    output_dir.mkdir(parents=True, exist_ok=True)

    for folder_name, entries in grouped.items():
        gallery_entries = []
        for rel_path, entry in sorted(entries, key=lambda x: str(x[0])):
            gallery_entries.append(build_gallery_entry(rel_path, entry))

        output_data = {"gallery": gallery_entries}

        output_path = output_dir / f"{folder_name}.yaml"
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(output_data, f, allow_unicode=True, sort_keys=False)

        print(f"✅ {folder_name}: {len(gallery_entries)} Bilder → {output_path}")

if __name__ == "__main__":
    generate_gallery_files()

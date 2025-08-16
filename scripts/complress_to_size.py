from PIL import Image
import io
import os

def jpeg_to_webp_target_size(input_path, output_path, target_kb=500, tolerance_kb=5):
    """
    Convert JPEG to WebP aiming for target_kb size, adjusting quality iteratively.
    tolerance_kb: acceptable size error in KB.
    """
    img = Image.open(input_path).convert("RGB")

    start_size_kb = os.path.getsize(input_path) / 1024
    print(f"Starting size: {start_size_kb:.1f} KB")

    target_bytes = target_kb * 1024
    tolerance_bytes = tolerance_kb * 1024

    # Start binary search on quality between 1 and 100
    low, high = 1, 100
    best_quality = None
    best_data = None

    while low <= high:
        mid = (low + high) // 2
        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=mid, method=6)  # method=6 gives better compression
        size = buf.tell()

        if abs(size - target_bytes) <= tolerance_bytes:
            # Close enough
            best_quality = mid
            best_data = buf.getvalue()
            break

        if size > target_bytes:
            # Too big → lower quality
            high = mid - 1
        else:
            # Too small → increase quality
            low = mid + 1

        # Keep best candidate close to target
        if best_data is None or abs(size - target_bytes) < abs(len(best_data) - target_bytes):
            best_quality = mid
            best_data = buf.getvalue()

    # Write result
    with open(output_path, "wb") as f:
        f.write(best_data)

    final_size_kb = len(best_data) / 1024
    print(f"Saved {output_path} at quality {best_quality} → {final_size_kb:.1f} KB")

if __name__ == "__main__":
    jpeg_to_webp_target_size("D:\\projects\\islandhunde-ostsee\\static\\images\\magni\\islandhund-schwarz-weiss-stehend.jpeg", "islandhund-schwarz-weiss-stehend.webp", target_kb=500, tolerance_kb=5)

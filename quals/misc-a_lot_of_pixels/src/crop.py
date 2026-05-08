from PIL import Image
import numpy as np

def crop_and_keep_near_gray(
    image_path,
    output_path,
    center_x,
    center_y,
    size=1000,
    target=(127,127,127),
    tolerance=50,
    transparent=False
):
    """
    Crops a square region around (center_x, center_y) and keeps only pixels
    whose color is within `tolerance` of `target` (default: (127,127,127)).
    Other pixels are set to black or transparent.
    """
    img = Image.open(image_path).convert("RGB")
    width, height = img.size

    half = size // 2
    left = max(0, min(center_x - half, width - size))
    upper = max(0, min(center_y - half, height - size))
    right = left + size
    lower = upper + size

    cropped = img.crop((left, upper, right, lower))
    arr = np.array(cropped, dtype=np.int16)  # use int16 to avoid overflow

    # Compute per-channel absolute difference from target
    diff = np.abs(arr - np.array(target))
    mask = np.all(diff <= tolerance, axis=-1)

    if transparent:
        # Add alpha channel and make others transparent
        rgba = np.dstack((arr.astype(np.uint8), mask.astype(np.uint8) * 255))
        rgba[~mask] = [0, 0, 0, 0]
        result = Image.fromarray(rgba, "RGBA")
    else:
        # Make non-matching pixels black
        arr[~mask] = [0, 0, 0]
        result = Image.fromarray(arr.astype(np.uint8))

    result.save(output_path)
    print(f"Saved cropped image with near-gray pixels to: {output_path}")
    print(f"Crop box: left={left}, upper={upper}, right={right}, lower={lower}")
    print(f"Color tolerance: ±{tolerance}")

    return result


if __name__ == "__main__":
    image_path = "heheheha.png"
    output_path = "cropped_near_gray.png"
    x, y = 4850, 1600  # example coordinate

    crop_and_keep_near_gray(image_path, output_path, x, y, tolerance=1, transparent=True)


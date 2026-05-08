from PIL import Image

def diff_to_png(img1_path, img2_path, output_path):
    # Load both images
    img1 = Image.open(img1_path).convert("RGB")
    img2 = Image.open(img2_path).convert("RGB")

    if img1.size != img2.size:
        raise ValueError("Images must have the same dimensions")

    width, height = img1.size

    # Prepare an RGBA output (for transparency)
    out = Image.new("RGBA", (width, height))
    out_pixels = out.load()

    px1 = img1.load()
    px2 = img2.load()

    # Define orange (diff) and transparent (same)
    ORANGE = (255, 165, 0, 255)
    TRANSPARENT = (0, 0, 0, 0)

    for y in range(height):
        for x in range(width):
            if px1[x, y] == px2[x, y]:
                out_pixels[x, y] = TRANSPARENT
            else:
                out_pixels[x, y] = ORANGE

    out.save(output_path, format="PNG")


# Example usage
diff_to_png("test.jpg", "test1.jpg", "diff.png")


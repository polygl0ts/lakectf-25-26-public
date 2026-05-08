from PIL import Image
import sys
num_frames = 4

def encode_16x16_bw_animation(path):
    # Load image
    img = Image.open(path).convert("RGB")
    # Check size
    if img.size != (16*num_frames, 16):
        raise ValueError(f"Image must be 16x16, got {img.size}")

    data = []
    for shift_x in range(num_frames):
        for y in range(16):
            # Each row produces exactly 2 bytes
            byte1 = 0
            byte2 = 0

            for x in range(16):
                r, g, b = img.getpixel((x+16*shift_x, y))

                # Validate black or white
                if (r, g, b) not in [(0, 0, 0), (255, 255, 255)]:
                    raise ValueError(
                        f"Invalid pixel at {(x,y)}: {(r,g,b)} — must be pure black or pure white"
                    )

                # Bit value: 1 = black, 0 = white
                bit = 1 if r == 0 else 0

                # First 8 pixels → byte1, next 8 → byte2
                if x < 8:
                    byte1 |= (bit << (7 - x))
                else:
                    byte2 |= (bit << (15 - x))

            data.append(byte1)
            data.append(byte2)

    return bytes(data)
def decode_bytes_to_animation(data, out_path):
    """
    data: bytes-like object of length 32
    out_path: output image file (PNG recommended)
    """

    # Validate length
    if len(data) != 32*num_frames:
        raise ValueError(f"Expected 128 bytes for a 16x16 animation, got {len(data)}")

    # Create empty 16x16 RGB image
    img = Image.new("RGB", (64, 16))

    # Decode row by row
    byte_index = 0
    for shift_x in range(num_frames):
        for y in range(16):
            byte1 = data[byte_index]
            byte2 = data[byte_index + 1]
            byte_index += 2

            # Decode 8 pixels from byte1 (MSB = leftmost)
            for x in range(8):
                bit = (byte1 >> (7 - x)) & 1
                # 1 = black → (0,0,0), 0 = white → (255,255,255)
                color = (0, 0, 0) if bit == 1 else (255, 255, 255)
                img.putpixel((x+shift_x*16, y), color)

            # Decode 8 pixels from byte2
            for x in range(8, 16):
                bit = (byte2 >> (15 - x)) & 1
                color = (0, 0, 0) if bit == 1 else (255, 255, 255)
                img.putpixel((x+shift_x*16, y), color)

    img.save(out_path)
    print(f"Image saved to {out_path}")
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python encode_bw_16x16.py image.png")
        sys.exit(1)
    

    encoded = encode_16x16_bw_animation(sys.argv[1])
    encoded = bytes.fromhex("000000000000644c86d085508450644c144214421442644c0000000000000000ffffffffffffdfffdfffdfbfdf7fc6f9dab7da1bdbbddbb3ffff1ffcffffffff80008000800080008000830a8495b495c695a5959495e315800000e080008000ffffffffffffffffffffffffebff88b76ab76acf6aef9a9ffffffff0ffffffff")
    new = bytes([a ^ 255 for a in encoded])
    decode_bytes_to_animation(new,"out.png")
    print("Byte array:", list(encoded))
    print("Hex:", encoded.hex())

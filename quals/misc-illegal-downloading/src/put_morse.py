from PIL import Image, ImageDraw, ImageFont
import random

# Morse code dictionary
MORSE_CODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....',
    '7': '--...', '8': '---..', '9': '----.', '_': "..--.-"
}

def text_to_morse(text):
    text = text.upper()
    return ' '.join(MORSE_CODE.get(c, '') for c in text if c in MORSE_CODE)

def darken_pixel(pixel):
    # Subtract 1 from each channel, clamp at 0
    return tuple(max(0, c - 1) for c in pixel[:3])

def draw_morse_on_image(image_path, text, dot_size=5, dash_size=15, spacing=5):
    img = Image.open(image_path).convert('RGB')
    width, height = img.size

    # Create a mask image to draw Morse code
    mask = Image.new('1', img.size, 0)  # 1-bit mask
    draw = ImageDraw.Draw(mask)

    morse = text_to_morse(text)
    
    # Random starting position
    x = random.randint(0, max(0, width - (len(morse) * (dash_size + spacing))))
    y = random.randint(0, max(0, height - dash_size))
    print(x,y)
    for symbol in morse:
        if symbol == '.':
            draw.ellipse((x, y, x + dot_size, y + dot_size), fill=1)
            x += dot_size + spacing
        elif symbol == '-':
            draw.rectangle((x, y, x + dash_size, y + dot_size), fill=1)
            x += dash_size + spacing
        else:
            # space between letters
            x += dash_size

        # Wrap to next line if necessary
        if x >= width - dash_size:
            x = 0
            y += dash_size + spacing
            if y >= height - dash_size:
                break  # stop if no space left

    # Apply mask: darken pixels under the Morse code
    pixels = img.load()
    mask_pixels = mask.load()
    for i in range(width):
        for j in range(height):
            if mask_pixels[i, j]:
                pixels[i, j] = darken_pixel(pixels[i, j])

    return img

# Example usage
result = draw_morse_on_image("test.jpg", "W3ll_1_h0p3_", dot_size=4, dash_size=8, spacing=7)

result.save("test1.jpg", quality=100, subsampling=0, optimize=False)


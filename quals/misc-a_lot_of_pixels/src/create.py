"""
writing flag EPFL{7h15_15_7h3_r1gh7_0n3!_h4h4h4h4} to 4850 1600
writing flag EPFL{7h15_15_n07_7h3_fl4g...} to 100 100
writing flag EPFL{7ry_4g41n} to 3000 1000
writing flag EPFL{h3h3h3h4} <- no flag to 6969 6969


Image saved!
"""
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random

# Create random image
W, H = 10000, 10000
arr = np.random.randint(0, 256, (H, W, 3), dtype=np.uint8)
def add_flag(flag, x = random.randint(0, W-200), y = random.randint(0, H-50), size=7, color = [127, 127, 127]):
    global arr
    # Create mask for text
    text_mask = Image.new("1", (W, H), 0)  # 1-bit: no antialiasing
    draw_mask = ImageDraw.Draw(text_mask)
    font = ImageFont.truetype("DejaVuSansMono.ttf", size)
    print("writing flag", flag, "to", x,y)
    draw_mask.text((x, y), flag, fill=1, font=font)

    # Convert mask to array and apply gray
    mask_arr = np.array(text_mask, dtype=bool)
    arr[mask_arr] = color  # fill with pure gray

add_flag("EPFL{7h15_15_7h3_r1gh7_0n3!_h4h4h4h4}")
add_flag("EPFL{7h15_15_n07_7h3_fl4g...}", 100, 100, size=20, color=[30, 100, 200])
add_flag("EPFL{7ry_4g41n}", 3000, 1000, size=16, color=[2, 100, 0])
add_flag("EPFL{h3h3h3h4} <- no flag", 6969, 6969, size=18, color=[255, 165, 0])

img = Image.fromarray(arr)

img.save("random_flag_image_graytext.png")

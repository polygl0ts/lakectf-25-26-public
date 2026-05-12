import random

def get_choices(base_digit):
    # Digits within ±1 to ±3 (mod 10)
    close_digits = []
    for i in range(1, 4):
        close_digits.append((base_digit + i) % 10)
        close_digits.append((base_digit - i) % 10)

    # Remove duplicates (just in case)
    close_digits = list(set(close_digits))

    # Other digits = remaining ones
    all_digits = set(range(10))
    other_digits = list(all_digits - set(close_digits))

    return close_digits, other_digits


def generate_code(base_code):
    result = ""
    special_numbers = ["000000","111111","222222","333333","444444","555555","666666","777777","888888","999999"]
    if random.random() < 0.9:
        for digit_char in base_code:
            base_digit = int(digit_char)
            close_digits, other_digits = get_choices(base_digit)

            if random.random() < 0.7:
                chosen = random.choice(close_digits)

            else:
                chosen = random.choice(other_digits)

            result += str(chosen)
    else:

        result += str(random.choice(special_numbers))
    return result


# Example usage
base_code = "111754"
new_code = generate_code(base_code)

with open("logs.txt", "w") as f:
    for i in range(100000):
        new_code = generate_code(base_code)
        f.write(new_code+"\n")
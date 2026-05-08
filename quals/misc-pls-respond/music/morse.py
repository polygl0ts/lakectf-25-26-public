MORSE = {
    'A': ".-",    'B': "-...",  'C': "-.-.",  'D': "-..",
    'E': ".",     'F': "..-.",  'G': "--.",   'H': "....",
    'I': "..",    'J': ".---",  'K': "-.-",   'L': ".-..",
    'M': "--",    'N': "-.",    'O': "---",   'P': ".--.",
    'Q': "--.-",  'R': ".-.",   'S': "...",   'T': "-",
    'U': "..-",   'V': "...-",  'W': ".--",   'X': "-..-",
    'Y': "-.--",  'Z': "--..",
    '0': "-----", '1': ".----", '2': "..---", '3': "...--",
    '4': "....-", '5': ".....", '6': "-....", '7': "--...",
    '8': "---..", '9': "----."
}

def text_to_morse(text):
    """Convert text to Morse code (letters separated by spaces)."""
    result = []
    for ch in text.upper():
        if ch == " ":
            result.append("")   # word separator: will create double space
        elif ch in MORSE:
            result.append(MORSE[ch])
    return " ".join(result)

def morse_to_custom(morse):
    """Convert Morse to custom alphabet: .->c2, - ->c1, space->r2"""
    out = []
    for ch in morse:
        if ch == '.':
            out.append("c4")
        elif ch == '-':
            out.append("c2")
        elif ch == ' ':
            out.append("r2")
    return "".join(out)
import sys
def main():
    if len(sys.argv) < 2:
        print("Usage: morse_encode.py <text>")
        sys.exit(1)

    text = " ".join(sys.argv[1:])
    morse = text_to_morse(text)
    custom = morse_to_custom(morse)

    print(custom)

if __name__ == "__main__":
    main()
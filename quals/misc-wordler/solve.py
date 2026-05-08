from pwn import remote, process
import sys
import re

# Configuration
WORD_LIST_FILE = "word_list.txt"


def load_words():
    try:
        with open(WORD_LIST_FILE, "r") as f:
            return [w.strip().upper() for w in f.read().splitlines()]
    except FileNotFoundError:
        print(f"Error: {WORD_LIST_FILE} not found.")
        sys.exit(1)


def parse_ansi(text):
    """Parses the colored output to determine state (Green/Yellow/Gray) and letter."""
    # ANSI codes used in challenge
    GREEN = "92m"
    YELLOW = "93m"
    GRAY = "90m"

    results = []
    # Regex to capture color code and the letter
    # Matches: \033[92mA\033[0m
    matches = re.findall(r'\x1b\[(.*?)(\w)\x1b\[0m', text)

    for color_code, letter in matches:
        if GREEN in color_code:
            results.append((letter, "GREEN"))
        elif YELLOW in color_code:
            results.append((letter, "YELLOW"))
        else:
            results.append((letter, "GRAY"))
    return results


def solve():
    all_words = load_words()

    # Start the challenge process
    #p = subprocess.Popen(CMD, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p = remote("chall.polygl0ts.ch",6052)
    #p = process(["python3","wordle.py"])
    # Read initial output to get structure
    buffer = ""
    while "Structure:" not in buffer:
        char = p.readline()
        if not char: break
        buffer += char.decode()

    # Parse Structure (e.g., Structure: ■■■■■_■■■■)
    structure_line = [line for line in buffer.split('\n') if "Structure:" in line][0]
    print(structure_line)
    structure_str = structure_line.split(": ")[1].strip()

    # Calculate lengths of individual words
    # e.g., "■■■■_■■■" -> [4, 3]
    word_lengths = [len(part) for part in structure_str.split('_')]
    total_letters = sum(word_lengths)

    print(f"[*] Structure identified: {structure_str}")
    print(f"[*] Word lengths: {word_lengths}")

    # Initialize candidates for each slot
    # slots[0] = all words of length matching word_lengths[0]
    slots = []
    for length in word_lengths:
        candidates = [w for w in all_words if len(w) == length]
        slots.append(candidates)

    print(f"[*] Candidates per slot initialized. Starting solve loop...")

    for turn in range(6):
        # 1. Generate Guess
        # We pick the first available candidate for each slot
        current_guess_parts = []
        for i, candidates in enumerate(slots):
            if not candidates:
                print(f"[!] Error: No candidates left for slot {i}!")
                p.close()
                return
            current_guess_parts.append(candidates[0])

        full_guess_str = "".join(current_guess_parts)
        print(f"[-] Turn {turn + 1} Guessing: {full_guess_str}")

        # 2. Send Guess
        p.sendline(full_guess_str.encode())

        # 3. Read Feedback
        feedback_line = ""
        while True:
            line = p.readline().decode()
            if "You win!" in line:
                print(f"\n[+] {line.strip()}")
                return True
            if "\x1b[" in line and "Structure" not in line:  # Detect colored line
                feedback_line = line.strip()
                break

        # 4. Process Logic
        parsed_feedback = parse_ansi(feedback_line)

        # We need to map the flat feedback list back to our word slots
        # e.g. feedback index 0-4 is slot 0, 5-9 is slot 1...
        global_idx = 0

        # Identify letters that are DEFINITELY in the solution (Green/Yellow)
        # to avoid removing them if they appear as Gray elsewhere (duplicate letter logic)
        confirmed_letters = set(char for char, color in parsed_feedback if color in ["GREEN", "YELLOW"])

        for slot_idx, length in enumerate(word_lengths):
            # Extract the feedback chunk for this specific word
            slot_feedback = parsed_feedback[global_idx: global_idx + length]
            global_idx += length

            # Filter candidates for this slot
            new_candidates = []
            for word in slots[slot_idx]:
                possible = True

                for i, (char, color) in enumerate(slot_feedback):
                    if color == "GREEN":
                        # Hard constraint: Word must have this char at this position
                        if word[i] != char:
                            possible = False
                            break
                    elif color == "GRAY":
                        # Soft constraint: Word likely shouldn't contain this char
                        # UNLESS it is a confirmed letter (handling double letter edge cases roughly)
                        if char not in confirmed_letters and char in word:
                            possible = False
                            break
                        # If it was gray here, it strictly cannot be at this position
                        if word[i] == char:
                            possible = False
                            break

                if possible:
                    new_candidates.append(word)

            slots[slot_idx] = new_candidates
            print(f"    Slot {slot_idx}: Reduced to {len(slots[slot_idx])} candidates")
    p.close()
    return False


if __name__ == "__main__":
    i = 0
    while True:
        i += 1
        if solve():
            print(f"Needed {i} attempts")
            break
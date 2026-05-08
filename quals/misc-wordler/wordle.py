#!/usr/bin/env -S python3 -u

import random

words = open("word_list.txt", "r").read().splitlines()
SOLUTION = random.choice(words)
while len(SOLUTION) < 26:
    SOLUTION+="_"+random.choice(words)

COLORS = {
    "GREEN":  "\033[92m", # Correct letter, correct place
    "YELLOW": "\033[93m", # Correct letter, wrong place
    "GRAY":   "\033[90m", # Letter not in solution
    "RESET":  "\033[0m"   # Resets color to default
}

def check_guess(guess, solution):    
    solution_upper = solution.upper()
    guess_upper = guess.upper()
    
    solution_letters = solution_upper.replace('_', '')
    guess_letters = guess_upper.replace('_', '')
    
    if guess_letters == solution_letters:
        print(f"{COLORS['GREEN']}{guess_letters}{COLORS['RESET']}")
        return True
            
    if len(guess_letters) != len(solution_letters):
        print(f"Guess must have {len(solution_letters)} letters. Try again.")
        exit() # git gud
    
    hint_states = ["GRAY"] * len(solution_letters)
    sol_remaining = list(solution_letters)
    
    for i in range(len(solution_letters)):
        if guess_letters[i] == solution_letters[i]:
            hint_states[i] = "GREEN"
            sol_remaining[i] = None
    
    for i in range(len(solution_letters)):
        if hint_states[i] == "GREEN":
            continue

        if guess_letters[i] in sol_remaining:
            hint_states[i] = "YELLOW"
            
            sol_index = sol_remaining.index(guess_letters[i])
            sol_remaining[sol_index] = None

    
    final_hint_parts = []
    letter_index = 0
    
    for char in solution_upper:
        if char == '_':
            final_hint_parts.append('_')
        else:
            state = hint_states[letter_index]
            guess_char = guess_letters[letter_index]
            
            color_code = COLORS[state]
            formatted_letter = f"{color_code}{guess_char}{COLORS['RESET']}"
            
            final_hint_parts.append(formatted_letter)
            letter_index += 1
            
    print("".join(final_hint_parts))
    return False

print(f"Welcome to Wordle! The solution has {len(SOLUTION.replace('_', ''))} letters.")
structure_hint = "".join(['_' if c == '_' else '■' for c in SOLUTION])
print(f"Structure: {structure_hint}")
print("-" * 30)

for _ in range(6):
    if check_guess(input("Your guess: "), SOLUTION):
        try: 
            from flag import FLAG
        except:
            FLAG = "EPFL{fake_flag}"
        print(f"You win! Heres the flag: {FLAG}")
        exit()

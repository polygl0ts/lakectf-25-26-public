#!/usr/bin/env python3
from pwn import *
import string

# --- CONFIGURATION ---
# Use 'process' for local testing if you have the file locally
# Use 'remote' for the actual CTF server
# target = process(['python3', './chall.py'])
HOST = 'chall.polygl0ts.ch'  # CHANGE THIS
PORT = 6001                  # CHANGE THIS

# Hide pwntools logs to keep output clean
context.log_level = 'error'

charset = string.digits # "0123456789"
flag = ""
flag_length = 32

print("[*] Starting Oracle Attack (Prefix Check)...")

for i in range(flag_length):
    print(f"[*] Brute-forcing position {i+1}/{flag_length}...")
    
    found_char = False
    
    for char in charset:
        try:
            # Connect to the server
            # r = process(['python3', './chall.py']) 
            r = remote(HOST, PORT)
            
            # Receive the initial banner "Don't even think to guess..."
            r.recvline()
            
            # Send our current known flag + the guess for the next digit
            guess = flag + char
            r.sendline(guess.encode())
            
            # Read the response
            response = r.recvall().decode()
            
            # Check if the server accepted it as a valid prefix
            if "Correct flag!" in response:
                flag += char
                found_char = True
                print(f"[+] Found digit: {char} | Current Flag: {flag}")
                r.close()
                break # Move to the next digit position
            
            r.close()
            
        except Exception as e:
            print(f"Error: {e}")
            if 'r' in locals(): r.close()

    if not found_char:
        print("[-] Failed to find the next digit. Is the flag length/charset correct?")
        break

print(f"\n[SUCCESS] Final Flag: EPFL{{{flag}}}")
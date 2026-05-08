#!/usr/bin/env python3
from pwn import *
import numpy as np
import re

# --- Configuration ---
# If running locally against the provided script:
# context.binary = python_script_name 
# p = process(['python3', 'challenge.py']) 

# If running against a remote server (replace HOST and PORT):
HOST = 'chall.polygl0ts.ch' 
PORT = 6002
p = remote(HOST, PORT)

def parse_matrix(text):
    """
    Parses the numpy string representation of the matrix X 
    into a usable numpy array.
    Example format: [[ 0.1+0.j   0.9+0.j]\n [ 0.2+0.j   0.8+0.j]]
    """
    # Clean the string: remove brackets and newlines
    clean_text = text.replace('[', '').replace(']', '').replace('\n', ' ')
    
    # Split by whitespace to get individual complex number strings
    # Filter out empty strings caused by multiple spaces
    elements = [complex(x) for x in clean_text.split() if x]
    
    # Reshape into 2x2 matrix
    return np.array(elements).reshape(2, 2)

# 1. Receive the preamble and the matrix X
p.recvuntil(b"matrix x = ")
matrix_str = p.recvuntil(b"\n\n", drop=True).decode()
print(f"[+] Received Matrix String: {matrix_str}")

X = parse_matrix(matrix_str)
print(f"[+] Parsed Matrix X:\n{X}")

# 2. Calculate Eigenvalues and Eigenvectors
# w: eigenvalues, v: eigenvectors (column v[:,i] is eigenvector i)
eigenvalues, eigenvectors = np.linalg.eig(X)

print(f"[+] Eigenvectors (Gate 1):\n{eigenvectors}")

# 3. Construct Gates
# Gate 1 maps Computational Basis -> Eigenbasis
# This is simply the matrix of eigenvectors
gate1 = eigenvectors

# Gate 2 maps Eigenbasis -> Computational Basis
# This is the inverse of Gate 1
gate2 = np.linalg.inv(gate1)

print(f"[+] Gate 2 (Inverse):\n{gate2}")

# 4. Send Matrices to Server
def send_matrix_elements(matrix):
    # Flatten to list: [a, b, c, d]
    flat = matrix.flatten()
    for val in flat:
        # Send as string representation of complex number
        p.sendlineafter(b"element:", str(val).encode())

print("[*] Sending Gate 1...")
send_matrix_elements(gate1)

print("[*] Sending Gate 2...")
send_matrix_elements(gate2)

# 5. Receive the Flag
# The server decrypts using our trick, so the measurement result 
# should be exactly the flag bits.
print("[*] Waiting for flag...")
p.recvuntil(b"measurement:") # skip the raw list output
p.recvline() # skip the newline

flag = p.recvall().decode().strip()
print(f"\n[SUCCESS] FLAG: {flag}")
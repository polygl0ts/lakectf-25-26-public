import json
import numpy as np
from sage.all import *

def get_negacyclic(coeffs, n, q, F):
    col = [0] * n
    for i, val in enumerate(coeffs):
        if i < n:
            col[i] = val
    
    cols = []
    curr = list(col)
    for _ in range(n):
        cols.append(list(curr))
        last = curr.pop()
        curr.insert(0, (-last) % q)
    
    return matrix(F, n, n, cols).transpose()

def poly_mult(p1, p2, n, q):
    res = [0] * (2 * n)
    for i, a in enumerate(p1):
        if a == 0: continue
        for j, b in enumerate(p2):
            if b == 0: continue
            res[i+j] = (res[i+j] + a * b) % q
    
    final = [0] * n
    for i in range(len(res)):
        if i < n:
            final[i] = (final[i] + res[i]) % q
        else:
            final[i-n] = (final[i-n] - res[i]) % q
    return final

def main():
    try:
        with open("keys.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("keys.json missing")
        return

    q = 3329
    n = 512
    k = 4
    F = GF(q)

    u1 = data["u_1"]
    u2 = data["u_2"]
    
    diff_flat = []
    for z in range(k):
        row = [(x - y) % q for x, y in zip(u1[z], u2[z])]
        diff_flat.extend(row)
    
    target = vector(F, diff_flat)

    blocks = [[None] * k for _ in range(k)]
    
    print("Constructing matrix...")
    for z in range(k):
        for j in range(k):
            c1 = [data["A_1"][i][j][z] for i in range(k)]
            c2 = [data["A_2"][i][j][z] for i in range(k)]
            diff = [(x - y) % q for x, y in zip(c1, c2)]
            blocks[z][j] = get_negacyclic(diff, n, q, F)

    M = block_matrix(blocks)
    
    print(f"Solving {M.nrows()}x{M.ncols()} system...")
    try:
        sol = M.solve_right(target)
    except ValueError:
        print("Solve failed.")
        return

    r_vals = [int(x) for x in sol]
    
    weight = sum(1 for x in r_vals if x != 0)
    print(f"Hamming weight: {weight}")

    r_polys = [r_vals[i*n : (i+1)*n] for i in range(k)]

    shared = [0] * n
    t1 = data["t_1"]
    
    for i in range(k):
        prod = poly_mult(t1[i], r_polys[i], n, q)
        shared = [(s + p) % q for s, p in zip(shared, prod)]
    
    v1 = data["v_1"]
    noisy_m = [(v - s) % q for v, s in zip(v1, shared)]
    
    bits = []
    low = q // 4
    high = 3 * q // 4
    
    for val in noisy_m:
        if low < val < high:
            bits.append(1)
        else:
            bits.append(0)
            
    chars = []
    for i in range(0, len(bits), 8):
        chunk = bits[i:i+8]
        if len(chunk) < 8: break
        val = int("".join(str(b) for b in chunk), 2)
        chars.append(chr(val))
        
    print("Flag:", "".join(chars))

if __name__ == "__main__":
    main()
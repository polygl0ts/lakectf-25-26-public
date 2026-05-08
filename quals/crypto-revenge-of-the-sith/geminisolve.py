import json
from sage.all import *

def solve():
    q, n, k = 251, 16, 2

    with open("keys.json", "r") as f:
        data = json.load(f)

    A_polys = data["A"]
    t_polys = data["t"]
    u_batch = data["u"]
    v_batch = data["v"]

    # Construct System Matrix M
    M_blocks = [[None for _ in range(k)] for _ in range(k)]
    for r_idx in range(k):
        for c_idx in range(k):
            coeffs = list(A_polys[c_idx][r_idx])
            cols = []
            curr = coeffs[:]
            for _ in range(n):
                cols.append(curr[:])
                curr = [-curr[-1]] + curr[:-1]
            M_blocks[r_idx][c_idx] = matrix(ZZ, cols).transpose()

    M = block_matrix(M_blocks)
    recovered_bits = []

    for u_polys, v_raw in zip(u_batch, v_batch):
        # Flatten u into a single vector
        u_vec = vector(ZZ, [c for poly in u_polys for c in poly])
        
        # Lattice Construction: Primal Attack
        # Basis B = [[qI, 0, 0], [M^T, I, 0], [-u, 0, 1]]
        dim_eq = k * n
        dim_unk = k * n
        
        B = matrix(ZZ, dim_eq + dim_unk + 1, dim_eq + dim_unk + 1)
        B.set_block(0, 0, q * identity_matrix(dim_eq))
        B.set_block(dim_eq, 0, M.transpose())
        B.set_block(dim_eq, dim_eq, identity_matrix(dim_unk))
        
        # Set bottom row
        for i in range(dim_eq):
            B[dim_eq + dim_unk, i] = -u_vec[i]
        B[dim_eq + dim_unk, dim_eq + dim_unk] = 1

        # Reduce
        L_red = B.BKZ(block_size=20)

        # Recover r
        found_r = None
        for row in L_red:
            if row[-1] == 1:
                found_r = row[dim_eq : dim_eq + dim_unk]
                break
            elif row[-1] == -1:
                found_r = -row[dim_eq : dim_eq + dim_unk]
                break
        
        if found_r is None:
            continue

        # Reshape r back into polynomials
        r_polys = [list(found_r[i*n : (i+1)*n]) for i in range(k)]

        # Decrypt: v - t^T * r
        # Compute dot product of polynomial vectors t and r
        shared = [0] * n
        for tp, rp in zip(t_polys, r_polys):
            # Polynomial multiplication mod x^n + 1
            res = [0] * (2 * n)
            for i, c1 in enumerate(tp):
                for j, c2 in enumerate(rp):
                    res[i+j] += c1 * c2
            
            curr_poly = [(res[i] - res[i+n]) % q if i < n else 0 for i in range(n)]
            shared = [(s + c) % q for s, c in zip(shared, curr_poly)]

        # Extract bits
        for val_v, val_s in zip(v_raw, shared):
            diff = (val_v - val_s) % q
            # Center lift and check distance from 0
            if diff > q/2: diff -= q
            recovered_bits.append(1 if abs(diff) > (q // 4) else 0)

    # Reconstruct Flag
    flag = ""
    for i in range(0, len(recovered_bits), 8):
        byte = recovered_bits[i:i+8]
        if len(byte) == 8:
            flag += chr(int("".join(map(str, byte)), 2))
            
    print(f"flag: {flag}")

if __name__ == "__main__":
    solve()
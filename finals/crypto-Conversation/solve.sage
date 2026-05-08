from sage.all_cmdline import *
from pwn import *
import json, re, base64

def poly_reduce(p, s, c):
    while True:
        new_p, changed = {}, False
        for (a, b, k), coeff in p.items():
            if not coeff: continue
            if b >= s and a >= 1:
                for dk, dc in [(1, coeff), (0, -c * coeff)]:
                    new_p[(a-1, b-s, k+dk)] = new_p.get((a-1, b-s, k+dk), 0) + dc
                changed = True
            else:
                new_p[(a,b,k)] = new_p.get((a,b,k), 0) + coeff
        p = {k: v for k, v in new_p.items() if v}
        if not changed: 
            return p

def poly_mul(p1, p2, s, c):
    r = {}
    for (a1,b1,k1), c1 in p1.items():
        for (a2,b2,k2), c2 in p2.items():
            r[(a1+a2, b1+b2, k1+k2)] = r.get((a1+a2, b1+b2, k1+k2), 0) + c1*c2
    return poly_reduce(r, s, c)

def kunihiro_attack(A, B, e, U, Y, m):
    Z, F = U * Y**2 + 1, {(0,0,1): 1, (1,1,0): A, (1,0,0): B}
    G = sorted([(kk-aa, bb, aa) for kk in range(m+1) for aa in range(kk+1) for bb in range(2)] +
               [(0, bb, kk) for kk in range(m+1) for bb in range(2, 2+kk)],
               key=lambda x: (x[0]+x[2], x[0], x[1]))
    idx = {mon: i for i, mon in enumerate(G)}
    
    Fpow = [{(0,0,0): 1}]
    for _ in range(m): 
        Fpow.append(poly_mul(Fpow[-1], F, 2, 1))
    
    M = Matrix(ZZ, len(G), len(G))
    for r, (ai, bi, ki) in enumerate(G):
        g = poly_reduce({(a+ai, b+bi, k): c for (a,b,k), c in Fpow[ki].items()}, 2, 1) if ai or bi else Fpow[ki]
        for (a,b,k), c in g.items():
            if (a,b,k) in idx:
                M[r, idx[(a,b,k)]] = c * (e**(m-ki)) * (U**a) * (Y**b) * (Z**k)
    
    polys = []
    for row in M.LLL():
        p, ok = {}, True
        for j, val in enumerate(row):
            if val:
                a,b,k = G[j]
                sc = (U**a) * (Y**b) * (Z**k)
                if val % sc != 0: 
                    ok = False
                    break
                p[(a,b,k)] = val // sc
        if ok and p: polys.append(p)
    return polys

def get_roots(polys, p0, q0, N):
    PR = PolynomialRing(ZZ, names=('u', 'v',)); (u, v,) = PR._first_ngens(2)
    sp = []
    for p in polys[:6]:
        biv = sum(c * binomial(k, i) * u**(a+i) * v**(b+2*i) for (a,b,k), c in p.items() for i in range(k+1))
        if biv:
            sp.append(biv)
        
    for poly in Ideal(sp).groebner_basis():
        if poly.is_univariate() and poly.variables()[0] == v:
            for y0, _ in poly.univariate_polynomial().roots(ring=ZZ):
                s = p0 + q0 + Integer(y0)
                d = s**2 - 4*N
                if d >= 0 and d.is_square():
                    p_c = (s + d.isqrt()) // 2
                    if N % p_c == 0: return int(p_c), int(N // p_c)


def _point_add(P1, P2, a_val, N):
    x1, y1, z1 = P1
    x2, y2, z2 = P2
    X = (x1*x2 + a_val*(y2*z1 + y1*z2)) % N
    Y = (x2*y1 + x1*y2 + a_val*z1*z2) % N
    Z = (y1*y2 + x2*z1 + x1*z2) % N
    return (X, Y, Z)

def _scalar_mult(k, P, a_val, N):
    res = (1, 0, 0)
    base = P
    while k > 0:
        if k % 2 == 1:
            res = _point_add(res, base, a_val, N)
        base = _point_add(base, base, a_val, N)
        k //= 2
    return res


context.log_level = 'debug'
#r = process(['python3', 'chall.py'])
r = remote('localhost', 6931)
#r = remote('unguessablechallsubdomain.polygl0ts.ch', 6931)

data = r.recvuntil(b'do you feel connected?')
# lowkey slopped this, couldnt figure it out myself, oops!
clean = re.sub(rb'\x1b\[[0-9;?]*[a-zA-Z]|\r|\xe2[\x94\x95][\x80-\xbf]', b'', data)
blob = re.sub(rb'\s', b'', re.search(rb'DATA:([A-Za-z0-9+/=\s]+)!', clean, re.DOTALL).group(1))
params = json.loads(base64.b64decode(blob))
N_hat, e_hat, N, e, a, C = params["N_hat"], params["e_hat"], params["N"], params["e"], params["a"], tuple(params["C"])


print("Factoring N_hat...")
K = 2**141
rem = N_hat % K
factors_rem = divisors(rem)

P_poly.<X> = PolynomialRing(Zmod(N_hat))
p_hat = None

for d in factors_rem:
    f = X * K + d
    f = f.monic()
    roots = f.small_roots(X=2**116, beta=0.4)
    if roots:
        p_hat = Integer(int(roots[0]) * K + d)
        if N_hat % p_hat == 0:
            print(f"Found p_hat: {p_hat}")
            break

q_hat = N_hat // p_hat
d_hat = pow(e_hat, -1, lcm(p_hat-1, q_hat-1))
p0 = p_hat
q0 = N // p0
A = 2*(p0+q0) - 2*(N+1)
B = (p0+q0)**2 - 2*(N+1)*(p0+q0) + (N+1)**2

Y = 2**142
U = int(4*e*(2**312) // N**2) + 1

print("Running Kunihiro lattice attack...")
for m_dim in [2, 3]:
    res = get_roots(kunihiro_attack(A, B, e, U, Y, m_dim), p0, q0, N)
    if res:
        print(f"Roots yoinked: {res}, we did it gamers")
        p, q = res
        
        phi_curve = (p - 1)**2 * (q - 1)**2
        d = inverse_mod(e, phi_curve)
        
        P_decrypted = _scalar_mult(d, C, a, N)
        
        m_val = int(P_decrypted[0])
        print(m_val)
        m_val = pow(m_val, d_hat, N_hat)
        print(m_val)
        key = m_val.to_bytes((m_val.bit_length() + 7) // 8, 'big')
        print(f"key: {key}")
        break

r.recvuntil([b'Type message > ', b'?\n\n'])
r.sendline(key)

r.interactive()

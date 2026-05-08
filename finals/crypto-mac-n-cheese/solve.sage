import time
import copy
from hashlib import shake_256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

TIMESTART = time.time()
set_random_seed(1)
# load("utils.sage")

param_set = {'label': 1, 'n': 3488, 'k': 2720, 'w': 64, 'm': 12, 'f': x ^ 12 + x ^ 3 + 1}


class Code:
    def __init__(self, m, t, n, modulus, irr_poly, g=None, support=None):
        self.m = m
        self.t = t
        self.n = n
        self.k = n - m * t
        self.setup_fields(modulus, irr_poly)
        if g is not None:
            self.goppa_poly = g
        else:
            self.goppa_poly = self.random_goppa_poly(t)
        if support is None:
            field_elems = list(self.F)
            start_support = field_elems[:n - (t * (m - 2) - 1)]
            end_support = field_elems[n - (t * (m - 2) - 1):n]
            shuffle(start_support)
            # shuffle(end_support)
            self.support = start_support + end_support
        else:
            self.support = support
        self.syndrome_poly_elems = self.prepare_syndrome_poly()
        self.H = self.build_parity_check()
        self._precompute_sqrt_x()

    def setup_fields(self, modulus, irr_poly):
        P = PolynomialRing(GF(2), "z")
        f = P(modulus)
        self.F = GF(2 ^ self.m, "z", modulus=f)
        self.R = PolynomialRing(self.F, "x")
        self.X = self.R.gen()
        irr_poly = self.R([self.F.from_integer(u) for u in irr_poly])
        assert irr_poly.is_irreducible()
        self.quotient_ring = self.R.quotient(irr_poly)

    def _precompute_sqrt_x(self):
        coeffs = self.goppa_poly.list()
        sqrt_in_field = lambda c: c ** (2 ** (self.m - 1))  # sqrt in GF(2^m)

        # Extract even/odd coefficients AND take sqrt of each in GF(2^m)
        even_coeffs = [sqrt_in_field(c) for c in coeffs[0::2]]
        odd_coeffs = [sqrt_in_field(c) for c in coeffs[1::2]]

        ae = self.R(even_coeffs)
        ao = self.R(odd_coeffs)
        _, _, ao_inv = self.goppa_poly.xgcd(ao)

        self._sqrt_x = ae * ao_inv % self.goppa_poly
        assert (self._sqrt_x * self._sqrt_x) % self.goppa_poly == self.X

    def random_goppa_poly(self, degree):
        coeffs = [self.F.random_element() for _ in range(degree)] + [self.F.one()]
        g = self.quotient_ring(coeffs).minpoly()
        return g

    def build_parity_check(self):
        cols = []
        for gamma in self.support:
            val = self.goppa_poly(gamma) ^ (-1)
            col_bits = []
            for i in range(self.t):
                elem = val * gamma ^ i
                coords = elem._vector_()
                col_bits.extend(list(coords))
            cols.append(col_bits)
        H_raw = matrix(GF(2), self.n, self.m * self.t, cols).T
        return H_raw.rref()

    def prepare_syndrome_poly(self):
        # Computing all possible syndromes to speed up key encapsulation
        elems = []
        for i, gamma in enumerate(self.support):
            denom = self.X - gamma
            _, _, inv = self.goppa_poly.xgcd(denom)
            inv = inv % self.goppa_poly
            elems.append(inv)
        return elems

    def compute_syndrome_poly(self, received):
        S = self.R(0)
        for i, gamma in enumerate(self.support):
            if received[i] == 1:
                S = (S + self.syndrome_poly_elems[i]) % self.goppa_poly
        return S

    def poly_sqrt_mod(self, f):
        # from https://crypto.stackexchange.com/questions/17988/algorithm-for-computing-square-roots-in-gf2n
        f = self.R(f) % self.goppa_poly
        coeffs = f.list()
        sqrt_in_field = lambda c: c ** (2 ** (self.m - 1))  # sqrt in GF(2^m)

        # Extract even/odd coefficients AND take sqrt of each in GF(2^m)
        even_coeffs = [sqrt_in_field(c) for c in coeffs[0::2]]
        odd_coeffs = [sqrt_in_field(c) for c in coeffs[1::2]]

        ae = self.R(even_coeffs)
        ao = self.R(odd_coeffs)

        # sqrt(f) = ae + sqrt(x) * ao, then reduce mod goppa_poly
        result = (ae + self._sqrt_x * ao) % self.goppa_poly

        assert (result * result) % self.goppa_poly == f, "sqrt failed"
        return result

    def patterson_error_locator(self, received):
        S_x = self.compute_syndrome_poly(received)
        if S_x == 0:
            return self.R(1)  # no errors
        _, _, S_x_inv = self.R(self.goppa_poly).xgcd(S_x)
        S_x_inv = S_x_inv % self.goppa_poly
        if S_x_inv == self.X:
            return self.X
        T = self.poly_sqrt_mod(S_x_inv + self.X)
        # EEA decode: find x,y with deg(x) <= t/2
        # Run EEA on (goppa_poly, T) stopping when remainder degree < t/2
        r0, r1 = self.R(self.goppa_poly), T % self.goppa_poly
        s0, s1 = self.R(0), self.R(1)
        while r1.degree() > self.t // 2:
            q = r0 // r1
            r0, r1 = r1, r0 - q * r1
            s0, s1 = s1, s0 - q * s1
        x_poly = r1
        y_poly = s1
        assert x_poly == y_poly * T % self.goppa_poly
        u = (x_poly ^ 2 + self.X * y_poly ^ 2)
        return u

    def find_errors(self, msg):
        errors = []
        error_locator = self.patterson_error_locator(msg)
        for i, gamma in enumerate(self.support):
            if error_locator(gamma) == 0:
                errors.append(i)
        return errors


class McEliece:

    def __init__(self, g=None, support=None):
        f = [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1]  # z^12 + z^3 + 1
        F = [2, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        # x^64 + x^3 + x + z
        self.code = Code(12, 64, 3488, f, F, g, support)
        self.pub_key = self.code.H

    def create_session_key(self):
        error_positions = sample(range(self.code.n), self.code.t)
        error_vector = vector(GF(2), [1 if i in error_positions else 0 for i in range(self.code.n)])
        encapped_key = self.pub_key * error_vector
        e = int("".join([str(v) for v in error_vector]), 2)
        C = int("".join([str(v) for v in encapped_key]), 2)
        SESSION_KEY_SIZE = int(128 / 8)
        session_key = shake_256(
            b"\x01" + e.to_bytes(ceil(self.code.n / 8)) + C.to_bytes(ceil(self.code.m * self.code.t / 8))).digest(
            SESSION_KEY_SIZE)
        return session_key, encapped_key

    def decap_key(self, encapped_key):
        encapped_key = vector(GF(2), encapped_key)
        n = self.code.n
        k = self.code.k
        mt = self.code.m * self.code.t
        v = vector(GF(2), list(encapped_key) + [0] * k)
        error_positions = self.code.find_errors(v)
        e = vector(GF(2), n, {i: 1 for i in error_positions})
        if sum([int(bit) for bit in e]) != self.code.t or self.code.H * e != encapped_key:
            return None
        e_int = int("".join(str(b) for b in e), 2)
        C_int = int("".join(str(b) for b in encapped_key), 2)
        SESSION_KEY_SIZE = 128 // 8
        session_key = shake_256(b"\x01" +
                                e_int.to_bytes(ceil(n / 8), "big") +
                                C_int.to_bytes(ceil(mt / 8), "big")).digest(SESSION_KEY_SIZE)
        return session_key


def generate_system(f, u, ff, Rg, Rg_squared, t):
    """
    generate the system of the form [f | x*f | ... | x^(u-1)*f| -Id]
    """
    A = matrix(ff, 2 * t, 2 * u - 1)
    for j in range(u):
        tmp_ = list(Rg_squared(f * x ^ j))
        for i in range(len(tmp_)):
            A[i, j] = tmp_[i]
    for i in range(u, 2 * u - 1): A[i - u, i] = -1
    return A


def generate_c2(H, I, t, m, F, c1):
    """
    generate  a codeword that has only one '1' coordintes on positions supp(c_1) \setminus I
    and has at most t ones on positions [1..n]\setminus I
    """
    n = H.ncols()
    Ntrials = 7000
    trial = 0
    full_rank_failures = 0

    supp_c1 = []
    for i in range(n):
        if (not i in I) and (c1[i] == 1): supp_c1.append(i)
    Habr = matrix(F, H.nrows(), t * m + 2)  # +const to hope for full row-rank
    counter = 0
    for j in range(n):
        if (j in I):
            for i in range(H.nrows()):
                Habr[i, counter] = H[i, j]
            counter += 1
    save_counter = counter

    while trial < Ntrials:
        new_columns = []
        counter = save_counter

        while counter < t * m + 2:  # +the same const to hope for full row-rank
            new_column = ZZ.random_element(0, n)
            if (not new_column in I) and (not new_column in new_columns) and (not new_column in supp_c1):
                for i in range(H.nrows()):
                    Habr[i, counter] = H[i, new_column]
                counter += 1
                new_columns.append(new_column)
        if Habr.rank() < t * m:
            trial += 1
            full_rank_failures += 1
            continue

        # for each i s.t. c1[i]==1, try to express c1[i] as a lin. combination of Habr and this lin. combination has <t+2 1's on notI
        # such linear combination will form c2
        for i in supp_c1:

            assert (not i in new_columns)

            # ith column
            columnH = [0] * (t * m)
            for j in range(t * m): columnH[j] = H[j, i]
            # print(Habr.ncols(), Habr.nrows(), t*m, Habr.rank())

            res = Habr.solve_right(vector(columnH))
            assert (len(res) == len(I) + len(new_columns))

            ctr = 0
            codeword = [0] * n
            codeword[i] = 1
            wt_res = 1
            for j in I:  # cols in Habr are positioned differently to cols in H, a loop over range(n) is wrong
                codeword[j] = res[ctr]
                ctr += 1
            for j in new_columns:
                codeword[j] = res[ctr]
                ctr += 1
                if codeword[j] == 1: wt_res += 1

            assert (H * vector(F, codeword) == vector(F, [0] * H.nrows()))

            if wt_res < t + 1:
                return codeword, i
        trial += 1
    print('Warning: ran out of trials in generate_c2')
    print('number of full_rank_failures:', full_rank_failures)
    return [], []


def generate_codeword(H, I, t, m, F):
    """
    generate a codeword that has at most t+1 1's on [1..n]\setminus I positions
    """
    n = H.ncols()

    Ntrials = 300
    trial = 0
    while trial < Ntrials:

        notI = []  # copy.deepcopy(i_star)
        counter = len(notI)

        while counter < (t * m + 1) - len(I):
            tmp_pos = ZZ.random_element(0, n)
            if (not tmp_pos in I) and (not tmp_pos in notI):
                notI.append(tmp_pos)
                counter += 1

        Habr = matrix(F, H.nrows(), t * m + 1)

        counter = 0
        for j in range(n):
            if (j in I) or (j in notI):
                for i in range(H.nrows()):
                    Habr[i, counter] = H[i, j]
                counter += 1

        Habr_kernel = Habr.transpose().kernel().basis()

        for v in Habr_kernel:

            counter = 0
            codeword = [0] * n
            for i in range(n):
                if (i in I) or (i in notI):
                    codeword[i] = v[counter]
                    counter += 1

            # if (not i_star==[]) and (codeword[i_star[0]]==0): continue

            n_ones = sum([int(codeword[i]) for i in notI])
            # if (not i_star==[]):
            #    assert(codeword[i_star[0]]==1)

            assert (H * vector(F, codeword) == vector(F, [0] * H.nrows()))

            if n_ones < t + 2:  # condition assures that we will be able to find the unknown alphas
                return codeword

        trial += 1
    print('Warning: ran out of trials in generate_codeword()')
    return []


def obtain_alphas(codeword, I, notI, Lleaked, ff, Rg, Rg_squared):
    """
        obtain the *set* A_codewords  -- alpha_i's for i \in notI
    """

    known_part = 0
    counter = 0
    for i in I:
        if codeword[i] == 1:
            known_part += 1 / Rg_squared(x - Lleaked[counter])
        counter += 1

    A = generate_system(known_part, len(notI), ff, Rg, Rg_squared, t)
    target = vector(ff, list(Rg_squared(known_part * x ^ (len(notI)) + (len(notI) % 2) * x ^ (len(notI) - 1))))
    try:
        res = A.solve_right(target)
    except:
        print("System failed, maybe just one-time but verify if it occurrs again")
        return []
    res_ = res[:len(notI)]
    res_roots = R(list(res_) + [1]).roots(ff)
    alphas = [res_roots[i][0] for i in range(len(res_roots))]

    return alphas


p = 2
F = GF(p)
kappa = param_set['m']
w = param_set["w"]
n = param_set["n"]
defining_poly = param_set['f']
ff.<z> = FiniteField(p ** kappa, modulus=defining_poly)
unordered_supp = list(ff)[:n]
R = PolynomialRing(ff, 'x')
x = R.gen()
SPLIT_STRING = b"\n---- present day, present time. haha. ----\n"


def pub_key_from_bytes(encoded_mat):
    num_bits = kappa * w * n
    num_bytes = ceil(num_bits / 8)
    assert num_bytes >= len(encoded_mat)
    s = int.from_bytes(encoded_mat, "big")
    binary_repr = Integer(s).digits(2)
    binary_repr = [0] * (num_bits - len(binary_repr)) + binary_repr
    rows = []
    for row_inv in range(kappa * w):
        rows.append(binary_repr[row_inv * n:(row_inv + 1) * n])
    reconstructed = matrix(GF(2), rows[::-1])
    return reconstructed


def recover_few_possible_g(leak):
    poss = set()
    indices_map = []
    for i in range(0, 2850):
        if i % 100 == 0:
            print(i)
        l = [u for u in factor(leak * (x - unordered_supp[i]) - 1)]
        if len(l) == 1 and (l[0][0].degree() == w) and l[0][0].is_irreducible():
            poss.add(l[0][0])
            indices_map.append((i, l[0][0]))
    return poss, indices_map

with open("wired_transmission.txt", "rb") as f:
    text = f.read()
    parts = text.split(SPLIT_STRING)
    assert len(parts) == 5
    H = pub_key_from_bytes(parts[0])
    enc_flag = parts[1]
    encapped_key = eval(parts[2].decode())
    leak0 = eval(parts[3].decode().replace("^", "**"))
    leak1 = eval(parts[4].decode().replace("^", "**"))

print("Starting to recover g from first leak")
poss_g0, indices0 = recover_few_possible_g(leak0)
print("Recovering g from second leak")
poss_g1, indices1 = recover_few_possible_g(leak1)
g = poss_g0.intersection(poss_g1)
assert len(g) == 1
g = list(g)[0]
print([unordered_supp[u[0]] for u in indices0 if u[1] == g][0])
print([unordered_supp[u[0]] for u in indices1 if u[1] == g][0])
print("============\n Recovered g:\n")
print(g)

i1337 = [unordered_supp[u[0]] for u in indices0 if u[1] == g][0]
i1420 = [unordered_supp[u[0]] for u in indices1 if u[1] == g][0]
I = [1337, 1420] + list(range(n - (w * (kappa - 2) - 1), n))
sizeI = len(I)
Lleaked = [i1337, i1420] + unordered_supp[-639:]
assert len(Lleaked) == w * (kappa - 2) + 1
assert len(Lleaked) == len(I)
assert sorted(I) == I
# H, L, g = gen_instance(param_set,ff,F)
Rg = R.quotient(g, 'x')
Rg_squared = R.quotient(g * g, 'x')

t = g.degree()
assert t == w
m = param_set['m']
assert m == kappa
assert sizeI == (t * m) + 1 - 2 * t
k = param_set['k']
print('sizeI:', sizeI)
print('t:', t)


def obtain_common_alpha(c1, notI1, c2, notI2, I, Lleaked, ff, Rg, Rg_squared):
    """
        A_c1 \cap A_c2
    """

    alpha1 = obtain_alphas(c1, I, notI1, Lleaked, ff, Rg, Rg_squared)
    if alpha1 == []:
        return -1
    alpha2 = obtain_alphas(c2, I, notI2, Lleaked, ff, Rg, Rg_squared)

    if alpha2 == []:
        return -1

    intersection = list(set(alpha1) & set(alpha2))
    return intersection


def notI(I, c):
    """
        return supp(c_1)\setminus I
    """
    notI = []
    for i in range(len(c)):
        if (not i in I) and c[i] == 1: notI.append(i)

    return notI


def update_Lleaked(I, i_star, Lleaked, new_alpha):
    """
    insert i_star into Lleaked into the correct positions
    """
    i = 0
    while i_star > I[i] and i < len(I):
        i += 1
    n = len(Lleaked)
    pos_insert = i

    Lleaked_tmp = copy.deepcopy(Lleaked)

    Lleaked.append(0)
    Lleaked[pos_insert] = new_alpha

    for i in range(pos_insert, n):
        Lleaked[i + 1] = Lleaked_tmp[i]
    return Lleaked


def gen_parity(L, g):
    """
        generates the parity check matrix of GoppaCode(L, g)
        over the extension field
    """
    n = len(L)
    glist = list(g)
    t = g.degree()
    G = matrix(parent(glist[0]), t)
    for i in range(t):
        for k in range(i + 1):
            G[i, k] = glist[t - k]
    V = matrix.vandermonde(L).transpose()

    V1 = V[0:t]
    Gdiag = matrix.diagonal([1 / g(L[i]) for i in range(n)])
    # print(G)
    return V1 * Gdiag


def gen_parity_full(L, g, kappa, n, F, ff, echelonForm=True):
    """
        generates the parity check matrix of GoppaCode(L, g)
        over the base (binary) field
    """
    Hbar = gen_parity(L, g)
    V, from_V, to_V = ff.vector_space(F, map=True)
    H = matrix(F, kappa * Hbar.nrows(), n)
    for i in range(Hbar.nrows()):
        for j in range(n):
            tmp_vec = to_V(Hbar[i, j])
            for k in range(kappa):
                H[kappa * i + k, j] = tmp_vec[k]
    if echelonForm: H = H.echelon_form()
    return H


def recover_Hpriv_complete(H, g, Labr, F, ff, kappa, I):
    """
        computing a privite parity-check matrix
        by (1) creating an invertible submatrix of the public H and
        (2) generating a privite submatrix from the subset of Goppa points Labr
        and g. We then find an invertible transformation (U) between them.

        Assumes that len(Labr)==nrows+1. Uncomment the commented out lines for
        the function to work with any Labr>=nrows+1
    """
    # assert(dim<len(Labr))
    nrows = H.nrows()
    assert (len(Labr) > nrows)
    Hpub_abr_ = H[[i for i in range(nrows)], [j for j in range(H.ncols()) if j in I]]
    # assert(Hpub_abr_.ncols()==len(Labr))

    assert (len(Labr) == nrows + 1)
    for indicator in range(len(Labr)):
        # print(ind,[j for j in range(len(Labr)) if not j==ind])
        Hpub_abr = Hpub_abr_[[i for i in range(nrows)], [j for j in range(len(Labr)) if not j == indicator]]
        assert (Hpub_abr.nrows() == Hpub_abr.ncols())
        if Hpub_abr.is_invertible():
            break
    if indicator == len(Labr) - 1 and not Hpub_abr.is_invertible():
        print('could not find invertible Hpub_abr')
        return 0
    Hpriv_abr = gen_parity_full(Labr, g, kappa, len(Labr), F, ff, echelonForm=False)
    Hpriv_abr = Hpriv_abr[[i for i in range(nrows)], [j for j in range(len(Labr)) if not j == indicator]]
    # print('Hpriv_abr is constructed')
    U = Hpriv_abr * Hpub_abr.inverse()
    # print('U is constructed')

    Hpriv_candidate = U * H
    return Hpriv_candidate


new_alphas = []
new_positions = []
sizeI_ = sizeI
last_leakages = []
Hpriv_candidate = 0
side_elems = []
print("Now recovering 128 alphas one by one before recovering them all")
while sizeI_ < t * m + 1 or Hpriv_candidate == 0:
    c1 = generate_codeword(H, I, t, m, F)
    if c1 == []:
        continue
    notI1 = notI(I, c1)
    if len(notI1) > t:
        continue
    c2, i_star = generate_c2(H, I, t, m, F, c1)
    if i_star in new_positions or c2 == []:
        continue
    notI2 = notI(I, c2)

    new_alpha = obtain_common_alpha(c1, notI1, c2, notI2, I, Lleaked, ff, Rg, Rg_squared)
    if new_alpha == -1:
        continue
    if (not len(new_alpha) == 1) or (len(new_alpha) == 0):
        continue
    # assert(L[i_star]==new_alpha[0])
    new_alphas.append(new_alpha[0])
    new_positions.append(i_star)
    sizeI_ += 1
    if sizeI_ <= t * m - 9:
        Lleaked = update_Lleaked(I, i_star, Lleaked, new_alpha[0])
        I.append(i_star)
        I.sort()
    else:
        print("storing on the side now")
        side_elems.append((i_star, new_alpha[0]))
    print(sizeI_, i_star, new_alpha)
    if sizeI_ >= t * m + 1:
        print(new_positions)
        I_cpy = copy.deepcopy(I)
        Lleaked_cpy = copy.deepcopy(Lleaked)
        for side_elem in sample(side_elems, 10):
            Lleaked_cpy = update_Lleaked(I_cpy, side_elem[0], Lleaked_cpy, side_elem[1])
            I_cpy.append(side_elem[0])
            I_cpy.sort()
        print("phase 2 should start now")
        Hpriv_candidate = recover_Hpriv_complete(H, g, Lleaked_cpy, F, ff, kappa, I_cpy)
        if Hpriv_candidate == 0:
            print("one more number to be found")
        else:
            Lleaked = Lleaked_cpy
            I = I_cpy


# ========================================
# ========================================
def recover_all_alpha(Lleaked, g, Hpriv_candidate, ff, kappa, target_size):
    """
    Using a candindate for the privite parity-check matrix found in recover_Hpriv_complete,
    find all Goppa points by brute-forcing over the field ff
    """
    V, from_V, to_V = ff.vector_space(F, map=True)
    LeakedSet = set(Lleaked)
    nr = Hpriv_candidate.nrows() / kappa
    L_remaining = []
    column_set = Hpriv_candidate.columns()
    exit_flag = False
    for el in ff:
        if exit_flag: break
        if not el in LeakedSet:
            inv = 1 / g(el)
            vector_candidate = vector([inv * el ^ i for i in range(nr)])
            vector_candidate_bin_ = [to_V(ff(vector_candidate[i])) for i in range(nr)]
            tmp = []
            for x in vector_candidate_bin_: tmp += list(x)
            tmp = (vector(tmp))
            try:
                ind = column_set.index(tmp)
                L_remaining.append((ind, el))
                if len(L_remaining) == target_size: exit_flag = True
            except ValueError:
                continue
    return L_remaining


sizeI = sizeI_
assert sizeI == n - k + 1
assert Hpriv_candidate != 0
print("Recovering all remaining alphas")
completeL = recover_all_alpha(Lleaked, g, Hpriv_candidate, ff, kappa, k - 1)
assert len(completeL) == k - 1
for elem in completeL:
    Lleaked = update_Lleaked(I, elem[0], Lleaked, elem[1])
    I.append(elem[0])
    I.sort()
assert len(Lleaked) == n
print("SUCCESS: private key fully recovered")
cipher = McEliece(g, Lleaked)
session_key = cipher.decap_key(encapped_key)
assert session_key is not None
dec_flag = AES.new(session_key, AES.MODE_ECB).decrypt(enc_flag)
time_end = time.time()
print(f"Time needed for full solve: {time.time()-TIMESTART}")
print(unpad(dec_flag,16))


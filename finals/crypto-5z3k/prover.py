from sharing import interpolation_coeffs
from circuit import Circuit
from params import commitment, K, N, T, TAU_IN, TAU_OUT, CheckT, NU, Check, Input, Witness, RingCheckChallenge, gmul, gsum
from rng import Rng

import json

from pwn import process, remote, args
import tqdm


def PoW(io):
    io.recvline()
    p = process(["sh", "-c", io.recvline().decode().strip()])
    io.sendline(p.recvall().strip())

def start():
    if args.LOCAL:
        return process(["python", "verifier.py"])

    io = remote(args.HOST, args.PORT)
    PoW(io)
    return io


## Assume trivial sharing everywhere :)

class MulCheckParty:
    def __init__(self, party, seed):
        self.party = party
        eta_rng = Rng(seed)
        eta = [Check.sample(eta_rng) for _ in party.mults]
        self.x = list(map(gmul, eta, [x for x, _, _ in party.mults]))
        self.y = [y for _, y, _ in party.mults]
        self.z = gsum(map(gmul, eta, [z for _, _, z in party.mults]))

    def start_compress(self):
        chunklen = len(self.x) // NU
        aa = [self.x[i:i + chunklen] for i in range(0, len(self.x), chunklen)]
        bb = [self.y[i:i + chunklen] for i in range(0, len(self.x), chunklen)]
        cc = [gsum(map(gmul, a, b)) for a, b in zip(aa, bb)]
        for c in cc:
            self.party.input(c)
        self.stored_zi = cc[:]

        if chunklen == 1:
            # Randomize with v and w
            v = [Check.zero() for _ in aa[0]]
            aa.append(v)
            w = [Check.zero() for _ in bb[0]]
            bb.append(w)
            for hint in v + w:
                self.party.input(hint)
        self.stored_aa = aa[:]
        self.stored_bb = bb[:]

        # inject z_i
        alpha = [Check.exseq(i + 1) for i in range(2 * NU + 1)]
        for z_index in list(range(NU + 1, 2 * NU)) + ([2 * NU, 2 * NU + 1] if chunklen == 1 else []):
            coeffs = interpolation_coeffs(Check.exseq(z_index), alpha[:len(aa)])
            z = Check.zero()
            for i in range(len(aa[0])):
                f = gsum(map(gmul, coeffs, [e[i] for e in aa]))
                g = gsum(map(gmul, coeffs, [e[i] for e in bb]))
                z += f * g
            self.party.input(z)
            self.stored_zi.append(z)

    def continue_compress(self, seed: bytes):
        # Derive epsilon
        epsilon = Check.sample(Rng(seed))
        # update self.x, self.y, self.z
        alpha = [Check.exseq(i + 1) for i in range(2 * NU + 1)]
        coeffs = interpolation_coeffs(epsilon, alpha[:len(self.stored_aa)])
        self.x = [gsum(map(gmul, coeffs, [e[i] for e in self.stored_aa])) for i in range(len(self.stored_aa[0]))]
        self.y = [gsum(map(gmul, coeffs, [e[i] for e in self.stored_bb])) for i in range(len(self.stored_bb[0]))]
        coeffs = interpolation_coeffs(epsilon, alpha[:len(self.stored_zi)])
        self.z = gsum(map(gmul, coeffs, self.stored_zi))
        assert (gsum(map(gmul, self.x, self.y)) - self.z).is_zero()

class Party:
    def __init__(self, context_comm):
        self.last_commit = context_comm
        self.commit_buf = []
        self.openings = []
        self.view = []
        self.wires = []
        self.mults: list[tuple[CheckT, CheckT, CheckT]] = []

    def input(self, v):
        self.wires.append(v)
        self.view.append(v)
        self.commit_buf.append(v)

    def commit(self, *extra_inputs):
        comm = commitment([self.last_commit, *self.commit_buf, *extra_inputs])
        self.commit_buf = []
        self.last_commit = comm
        return comm

    def open(self, share, res):
        assert (share - res).is_zero()
        self.openings.append(share)
        self.commit_buf.append(share)
        return res

    def ring_check(self, rs):
        v = gsum(map(gmul, rs, self.wires)) + self.wires[-1] # mask is last
        self.open(v, v)
        self.wires = [w.truncate(Witness.base_ring()) for w in self.wires[:-1]]
        assert all(x.is_zero() for x in v.v[1:])
        return v.v[0] if v.v else Input.base_ring().zero()

    def mul(self, a, b, c):
        # We assume trivial sharings :)
        # c = self.wires[a] * self.wires[b]
        self.wires.append(c)
        self.view.append(c)
        self.commit_buf.append(c)
        self.mults.append((Check([self.wires[a]]), Check([self.wires[b]]), Check([c])))

    def add(self, a, b):
        self.wires.append(self.wires[a] + self.wires[b])

    def inv(self, a):
        self.wires.append(Witness.one() - self.wires[a])

    def mul_check(self, seed) -> MulCheckParty:
        return MulCheckParty(self, seed)


def commit_mulcheck(io, p: Party, nmults: int):
    io.recvuntil(b"Compression seed:")
    eta_seed = bytes.fromhex(io.recvline().strip().decode())
    running = p.mul_check(eta_seed)
    while nmults > 1:
        print("iter")
        assert nmults % NU == 0
        running.start_compress()
        comm = p.commit().hex()
        io.sendlineafter(b"Commitments? ", json.dumps([comm for _ in range(N)]).encode())
        io.recvuntil(b"Seed:")
        seed = bytes.fromhex(io.recvline().strip().decode())
        running.continue_compress(seed)
        nmults //= NU
    p.open(running.x[0], running.x[0])
    claim = running.x[0]
    p.open(running.x[0] * running.y[0] - running.z, Check.zero())
    io.sendlineafter(b"Rec claim? ", json.dumps(claim.to_json()).encode())

def find_assignment(circuit: Circuit):
    from sage.all import Zmod, PolynomialRing, Matrix, vector
    used: list[set[str]] = [{f"i{i}"} for i in range(128)]
    used.extend([set() for _ in range(128)])
    for gate in tqdm.tqdm(circuit):
        match gate:
            case ("MUL", a, b):
                used.append({f"m{a}_{b}"})
            case ("ADD", a, b):
                used.append(used[a] | used[b])
            case ("INV", a):
                used.append(used[a])
            case x:
                assert False, f"Unknown gate: {x}"

    vars = set()
    for o in circuit.outputs:
        vars |= used[o]

    PR = PolynomialRing(Zmod(2**K), list(vars) + ["FAIL"])
    gens = {str(g): g for g in PR.gens()}
    wires = [gens.get(f"i{i}", PR(0)) for i in range(128)]
    wires.extend([PR(0) for _ in range(128)])
    for gate in tqdm.tqdm(circuit):
        match gate:
            case ("MUL", a, b):
                wires.append(gens.get(f"m{a}_{b}", gens["FAIL"]))
            case ("ADD", a, b):
                wires.append(wires[a] + wires[b])
            case ("INV", a):
                wires.append(PR(PR.base_ring()(1)) - wires[a])
            case x:
                assert False, f"Unknown gate: {x}"

    def expr_to_row(e):
        row = [e.coefficient(gens[g]) for g in sorted(gens)]
        assert row[0].is_zero()
        return (row, -e.constant_coefficient())
    m = []
    b = []
    for o in circuit.outputs:
        if wires[o].is_zero(): continue
        r, c = expr_to_row(wires[o])
        m.append(r)
        b.append(c)
    m = Matrix(PR.base_ring(), m)
    b = vector(PR.base_ring(), b)
    sol = Matrix(PR.base_ring(), m).solve_right(vector(PR.base_ring(), b))
    return {str(g): int(sol[i]) for i, g in enumerate(sorted(gens))}

def prove(io, circuit: Circuit, mulvals: dict[str, int]):
    context_comm = commitment([b"ZK4Z2K", str(circuit)])
    p = Party(context_comm)
    for i in range(circuit.ninputs):
        p.input(Input([Input.base_ring()(mulvals.get(f"i{i}", 0))]))
    p.input(Input.zero())

    input_comm = p.commit()
    io.sendlineafter(b"Input commitments? ", json.dumps([input_comm.hex() for _ in range(N)]).encode())
    io.recvuntil(b"rng seed: ")
    ring_check_seed = bytes.fromhex(io.recvline().strip().decode())

    ro = Rng(ring_check_seed)
    ring_check_rs = [Input([Input.base_ring()(int(RingCheckChallenge.sample(ro)))]) for _ in range(circuit.ninputs)] # type: ignore
    rcval = p.ring_check(ring_check_rs)
    io.sendlineafter(b"Ring check output claim? ", str(int(rcval)).encode())

    for gate in tqdm.tqdm(circuit):
        match gate:
            case ("MUL", a, b):
                p.mul(a, b, Witness([Witness.base_ring()(mulvals.get(f"m{a}_{b}", 0))]))
            case ("ADD", a, b):
                p.add(a, b)
            case ("INV", a):
                p.inv(a)
            case x:
                assert False, f"Unknown gate: {x}"
    extwit_comm = p.commit().hex()
    io.sendlineafter(b"Extended witness commitments? ", json.dumps([extwit_comm for _ in range(N)]).encode())

    for o in circuit.outputs:
        assert(p.wires[o].is_zero())
        p.open(p.wires[o], p.wires[o])
        # p.open(Witness.zero(), Witness.zero())

    for _ in range(TAU_IN):
        commit_mulcheck(io, p, circuit.nmults)

    # commit to openings
    all_shares = []
    for v in p.openings:
        all_shares.extend([v for _ in range(N + 1)])
    io.sendlineafter(b"Global opening commitment? ", commitment(all_shares).hex().encode())
    for _ in range(T):
        io.recvuntil(b"Open party ")
        io.sendlineafter(b"? ", json.dumps([v.to_json() for v in p.view]).encode())


if __name__ == "__main__":
    io = start()
    with open("aes_128.txt") as f:
        CIRCUIT = Circuit.parse(f)
        CIRCUIT.outputs += list(range(128, 256))
        CIRCUIT.pad(NU)
    mulvals = find_assignment(CIRCUIT)
    for _ in range(TAU_OUT):
        print("TAU_OUT ITER")
        prove(io, CIRCUIT, mulvals)

    io.stream()

# Conversation

+ Author: meow
+ Category: crypto
+ Intended difficulty: medium
+ Solves during competition: 1/10

I wrote this challenge after finding a Pell Curves discussion at [AfricaCrypt 2025](https://eprint.iacr.org/2025/875.pdf), in which Nitaj takes a look over his *own* publication in the [Morocan Journal of Sciences](https://ced.fst-usmba.ac.ma/p/mjaga/wp-content/uploads/2026/01/vol4_V2.pdf), which is followed by him repeatedly farming this for content, which is lowkey a goated strategy.

Anyways after a while, Seck, the *coauthor of the original paper*, seems to have enough of his coauthor farming content on their work??? and [publishes his own attacks on it](https://eprint.iacr.org/2026/519.pdf), which is where this challenge came to be.

Then afterwards, I realised just leaking the top bits of a prime is cringe, so what way to leak the top bits? Implicitly leaking the bottom bits of course! im so smart please praise me.


## Overview

This challenge asks you to, in a relatively quick manner (5 minutes), crack a standard RSA and a **Cubic Pell Curve** variant of RSA.

The challenge generates two 256-bit primes $p$ and $q$ and constructs a 512-bit modulus $N$. It then encrypts our target secret in two distinct layers:
1.  **Standard RSA:** The secret is encrypted as $m \equiv \text{secret}^{e_{hat}} \pmod{\hat{N}}$, where $\hat{N} = \hat{p} \cdot \hat{q}$.
2.  **Cubic Pell Curve RSA:** The value $m$ is embedded into a point $P = (m, v, 0)$ on a Cubic Pell curve. This point is then scalar-multiplied by $e$ to produce the final ciphertext $C$.

To recover the flag, we need to first factorise $\hat{N}$.Then using information from that, we can factorise $N$, and from that we decrypt both layers.

## Part 1

We can quickly see that, although $\hat{N}$ may look like a 512-bit modulus, it is actually lying about its size.
```python
hint_size = 115
p_hint = p.bit_length() - hint_size # 141
p_hat = nextprime((p >> p_hint) << p_hint)
```
We can take a look at what $\hat{p}$ actually looks like: 
```python
bin(p_hat) = '0b1000001011010000010111011011010001010110001101110001000011100110111101101100111001011111011101111010111100001100001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000101001'
```
Because the latter half is almost entirely 0s, so we can name the lower 141 bits a small integer $d_p$ and express the primes as:

$$\hat{p} = X \cdot 2^{141} + d_p$$ $$\hat{q} = Y \cdot 2^{141} + d_q$$

Because $d_p$ and $d_q$ are so small, their product $d_p \cdot d_q$ fits easily within 141 bits. Thus, if we take $\hat{N} \pmod{2^{141}}$, the larger terms will zero out, leaving us with exactly $d_p \cdot d_q$:
$$\hat{N} \equiv d_p \cdot d_q \pmod{2^{141}}$$

With this, we can simply use Coppersmith's Method for Known Lower Bits to find the upper 141 bits by calling `small_roots()`the polynomial $f(x) = x \cdot 2^{141} + d_p \pmod{\hat{N}}$. Once we have $x$, we can reconstruct $\hat{p}$ and factor $\hat{N}$.

## Part 2

I stole this from the paper: https://eprint.iacr.org/2026/519.pdf.

I won't insult your intelligence; you got this. With this we can factorise $N$.

## Part 3

With $N$ successfully factored, the rest is standard crypto stuff:
1. Compute the order of the Cubic Pell curve: $\psi(N) = (p-1)^2(q-1)^2$.
2. Calculate the true private key: $d \equiv e^{-1} \pmod{\psi(N)}$.
3. Perform point scalar multiplication on the Cubic Pell curve using $d$ against the ciphertext point $C$ to recover $P = (m, v, 0)$.
4. Extract $m$, which is the RSA encrypted secret.
5. Use our factors of $\hat{N}$ from Step 1 to calculate $\hat{d} \equiv \hat{e}^{-1} \pmod{\text{lcm}(\hat{p}-1, \hat{q}-1)}$.
6. Decrypt $m$ using standard RSA decryption: $\text{secret} \equiv m^{\hat{d}} \pmod{\hat{N}}$.

then, sending it back gets us the flag.

## Part Richtext

im so sorry, but it looks so pretty...

I slopped this together, but I bet it's doable in a non-horrible way.
```python
clean = re.sub(rb'\x1b\[[0-9;?]*[a-zA-Z]|\r|\xe2[\x94\x95][\x80-\xbf]', b'', data)
blob = re.sub(rb'\s', b'', re.search(rb'DATA:([A-Za-z0-9+/=\s]+)!', clean, re.DOTALL).group(1))
```

<3

---

hope you enjoyed

-meow

# mac-n-cheese

+ Author: Martin_Who
+ Category: crypto
+ Intended difficulty: medium/hard
+ Solves during competition: 0/10

In the Classic McEliece KEM cryptosystem, the public parameters are the following:

- m: the size of the extension field
- t: the number of errors in the error vector
- n: the size of the error vector, with n <= 2^m
- k: k = n-m*t

The private key consists of 2 elements:
- A degree-t irreducible polynomial of degree t, named g, with coefficients in the polynomial ring of GF(2^m)
- A list of n distinct ordered elements from GF(2^m), named L

The public key is a binary matrix H of size m*t by n, which is the row-reduced parity-check matrix of the goppa code defined by (g,L)


# How to solve
The challenge consists of simply following the specs to encapsulate a key and reveals the following informations:
- The public key H
- The flag encrypted with the derived session key
- The encapsulated session key
- Two strange values used in the middle of the computation corresponding to leak0:=(x-L[1337])^-1 mod g, leak1:=(x-L[1420])^-1 mod g

## First step
First of all we can use the two leaks to recover the secret polynomial g and the values L[1337] and L[1442]

First, we know that leak0 * (x-L[1337]) = ((x-L[1337])^-1 mod g) * (x-L[1337]) = 1 + p * g, with some random unkown p.
However we don't know what L[1337] corresponds to.
THe only thing sure is that, since g is the goppa polynomial, it is irreducible and of degree t.

We can then compute leak0*(x-e) - 1 for every element e of the field (there are 2^12=4096 elements), and then factor this value. If we find a degree-t irreducible polynomial in the factors, this might (or might not) be g and the corresponding field element might (or not) be L[1337].

By repeating this with the second leak, we get another list of candidate for g, and by doing the intersection of the two candidates, we can narrow it down to a single g, hence recovering the secret polynomial!

We now have g, L[1337] and L[1420], but how do we recover the rest of the points?

## Second step
By looking at the setup of the key, we can see that actually the first t*(m-2)-1 (here = 639) elements of the field are not shuffled, i.e. their order remains unchanged. This means that we directly know their value simply by checking the first 639 elements of the field in sagemath with GF(2^m)[:639].

## The paper
Now we can turn over to a paper called "Breaking Goppa-Based McEliece with Hints", which (very conveniently xD) requires exactly our setup to recover the remaining points:
One the claims of this paper, is that with t*(m-2)+1 (here 641) points and the goppa polynomial, we can recover all other points in polynomial time.
Since we have 639 points from the ordering, L[1337] and L[1420], we have indeed 641 points and the polynomial. We can use their script by modifying it a little bit to recovering the remaining points.

## Final part
Finally, we can instantiate a McEliece cipher from the code with our recovered private key (g,L), and recover the session key from its encapsulation, thereby recovering the flag and solving the challenge!!


# Quantum Vernam cipher

#### You have to transform the qubit such that the encryption does not modify the qubit.

In the real quantum One time pad,you have a key $k = (k_1,k_2) \in \{0,1\}^{2n}$, and you apply $X^{k_1}Z^{k_2}$ and this is perfectly secure.

Here this scheme is insecure because we apply $(XZ)^k$. 

We want to write our vectors in a basis such that they won't be modified a lot by the encryption (or at least in a predictible way). The only choice is the eigenbasis of XZ, when we encrypt our 2D vector (our qubit), it will only be multiplied by the eigenvalue of XZ, that are $j$ and $-j$. This factor is canceled in the measurement protocol because we multiply the coefficients by their complex conjugate, which gives 1. Finally, we construct the second gate in order to swap back our qubits in our initial basis. 


We find as a 1st matrix:

$$
\begin{pmatrix}
1 & 1 \\
-j & j
\end{pmatrix}
$$


 which is given by the eignevectors of XZ.
 
The second matrix is the inverse matrix, which is also the conjugate transposed (as matrices are unitary)

$$
\begin{pmatrix}
1 & j \\
1 & -j
\end{pmatrix}
$$


If $k = 1$, the encryption will multiply our vector by $j$ or $-j$. So we can just swap back our qubit in the original basis before measurement and we get $(j, 0)$ if original qubit was 0, and $(0, -j)$ otherwise. In both case the measurement gives always the right output.

If $k = 0$, we multiply our vector by $U_1 \times (U_1)^{-1} = I$, which does nothing, so measurement always gives right output.

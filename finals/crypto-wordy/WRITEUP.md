### Wordy Writeup

+ Author: Ale
+ Category: crypto
+ Intended difficulty: medium
+ Solves during competition: 4/10

The idea for the challenge came to me while playing wordle. "If the NY times is not using a cryptographically safe RNG can we start winning wordle in 1 by playing enough days?". The usual RNG is a mersenne twister and the answer is that you can obviously crack it, after 624 full observations of its outputs.

However what if you only observe partial outputs? One output of a MT RNG is 32 bits while the wordlist size of wordle is 2315. In order to pick a wordle answer at random we only need 12 bits out of the 32. 

It turns out you can crack an MT twister as well by modelling the twist and state-transition operations with Z3. I did some empirical testing and ~1200 iterations was enough to recover the state from observations of only the 24 LSBs.

In my challenge, the 32 bits of the output are used to pick the answer for 2 games of wordle. The wordlist is 2315 words so if you're able to guess an answer you're going to get 11/12 bits out of 16 every game. Originally this was the setup so you'd have 8/10 missing bits for every 32 bit output. Turned out this was hard to crack so I added an additional 2 bits leak if you win the wordle. So now you get 13/14 out of 16 bits for every game, thus you only miss 4/6 bits out of the 32 bits output.

In order to guarantee a wordle win you can use an entropy-based algorithm like the one discussed in the video linked in the challenge description. This one is an example: https://github.com/afontenot/wordle-solver.

For the symbolic RNG cracker you can use existing libraries such as this one: https://github.com/icemonster/symbolic_mersenne_cracker

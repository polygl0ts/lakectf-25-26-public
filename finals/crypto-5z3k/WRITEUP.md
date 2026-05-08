# 5z3k

+ Author: Robin_Jadoul
+ Category: crypto
+ Intended difficulty: `¯\_(ツ)_/¯`
+ Solves during competition: 0/10

Find the flaw in the paper: the compression multcheck does not link to the previous instance, so you can inject whatever valid compression and get away with wrong multiplication results.
To find a valid cheating multiplication result, just solve the linear system.
You can simplify and speed things up a tiny bit by making all parties just have a trivial sharing (the underlying value itself).

See prover.py for an implementation.

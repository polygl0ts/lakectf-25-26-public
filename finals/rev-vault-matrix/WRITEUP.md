# Vault Matrix

+ Author: Flan
+ Category: rev
+ Intended difficulty: hard
+ Solves during competition: 2/10

## The challenge
There is a single binary, `challenge`, doing everything. It expects an 81-character string of digits `1-9`. Internally, it decrypts a small multithreaded VM bytecode blob and runs four VM threads to validate a killer sudoku. The valid 81-digit solution is then reused to restore an RC4-encrypted final stage and derive an AES-256 key. The program prints an `iv:ciphertext` blob, which must be decrypted to recover the flag.

## Solution
Reverse or emulate the VM to recover the constraints. The four VM threads validate rows, columns, 3x3 blicks, and cage sums. Solving the resulting killer sudoku gives the correct 81-digit key. Using this key, restore the encrypted code blob called after VM success. The recovered final-stage function derives an AES-256 key from the full 81-digit solution and embedded constants. Use that key with the printed IV and ciphertext to decrypt the flag.


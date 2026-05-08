#!/usr/bin/env -S python3 -u

flag = "15392948299929328383828399923990"

print("Don't even think to guess the flag by brute force, it is 32 digits long!")

user_input = input()



if not user_input.isdigit():
    print("Flag only contains digits!")
    exit()



index = 0

for char in user_input:
    if char != flag[index]:
        print("Wrong flag!")
        exit()
    index += 1

print("Correct flag!")

print("flag is : EPFL{" +user_input + "}")
# The lab

+ Author: KimiNoPanda
+ Category: misc
+ Intended difficulty: easy
+ Solves during competition: 7/10


## Overview

The challenge was a 2 part challenge but the second part of the challenge was not deployed as it was a little too guessy and does not fit for an 8 hour CTF. 

The two challenge was about you trying to infiltrate the enemy lab and in order to get information from this lab. I wanted to make the challenge such that it could be a "real" investigation that someone might have when encoutering this type of problem
Both challenge are misc but tend to be forensics (the second one is more forensics). 


## Challenge

In this challenge, you were given a log file in which you have registered code state after that scientist entered the lab. My first idea was that when people a reshuffling the code, they tend to not reshuffle well and do it quickly without thinking much as they are doing this every time that they want to enter the lab. 

Thus, imagine the real digit is 4, then when the scientist wants to reshuffle the code, he will just give a small push to roll the digit either to the right or to the left and this small push will change the digit by a small digit from 1 to 3. It is just like when you are locking your lugage code, you just roll it one in either direction. 
However, some people might doing other things like resetting all the digits to the same number like 000000 for a 6 digit-code. 

## Solution

The idea to solve the challenge is to draw the distribution of each digit separately and you will see that you have a digit that is between you "mountain" of reccurent digit and this digit will be the right one.
Run solve script and change array name, you will get a distribution.

## Second challenge

To give a hindsight, the second challenge was a chromium profile where you need to retrive some information from it.

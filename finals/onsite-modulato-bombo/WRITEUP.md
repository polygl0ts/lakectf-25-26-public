# Modulato Bombo

+ Author: Hackin7
+ Category: onsite
+ Intended difficulty: easy
+ Solves during competition: 8/10

Challenge is mainly an excuse to get me to finish working on my custom SDR with jiefeng.
Wanted to do an RF Sniffing Challenge

Context is that for super high speed signals, they are so fast that they can be picked up as RF waves. 
By receiving them on an SDR you can essentially retrieve information
However to make it simpler for participants, we modulate the signals for them.
This is still (surprisingly) relevant for wired communications, as it is more 

Also the challenge is defusing a bomb because I thought it'll be funny.


## Equipment

In this case we'll try to provide RF equipment, but the bulk of it is using the custom SDR I have on hand 
(mainly because I dont have time/ money/ my HackRF is in SG lol). 
The custom SDR would be connected to my computer with Waterfall already available (so that they )
They would look at the waterfall manually and decode the PIN, on self testing it is not super tedious and should be relatively enjoyable.

An Oscilloscope would also theoretically work for this challenge but they would not as easily solve it.


## Solve Path

Main Hint to the challenge is that High Speed Signals are essentially RF waves, and they can be sniffed by an SDR

1. Read through the documentation 
    1. Figure out the communication protocol (its just binary)
    2. Understand what modulation is about
2. Come on site and look at the bomb
3. Use the RF SDR, point it at the exposed wire
    1. Configure the frequency of the SDR such that it matches the modulated frequency ==this might be a bit of a giveaway, since the GUI has the frequency configuration==
    2. Look at the waterfall and decode the packets sent
    3. Alternative method is the oscilloscope (video record and tediously decode the modulation)
4. Enter the PIN and get the flag


## TODOs

Improve the GUI and the coolness factor of the challenge.
Wrap up the MCU board into a (safe) "bomb" like package
Improve the PIN Entry UI from Computer to on the MCU itself
The challenge is meant to be easy, so the solve path is rather straightforward, and hopefully everyone solves it.

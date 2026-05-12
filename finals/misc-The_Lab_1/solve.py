import random
import matplotlib.pyplot as plt
from collections import Counter

D1 = []
D2 = []
D3 = []
D4 = []
D5 = []
D6 = []

with open("logs.txt","r") as f:
    lines = f.readlines()
    for num_samples in lines:
        num_samples = num_samples.strip()
        
        D1.append(int(num_samples[0]))
        D2.append(int(num_samples[1]))
        D3.append(int(num_samples[2]))
        D4.append(int(num_samples[3]))
        D5.append(int(num_samples[4]))
        D6.append(int(num_samples[5]))

# Count frequencies
counts = Counter(D6)

digits = list(range(10))
frequencies = [counts[d] for d in digits]

# Plot
plt.figure()
plt.bar(digits, frequencies)
plt.xlabel("Digit")
plt.ylabel("Frequency")
plt.title("Digit Frequency Distribution")
plt.show()
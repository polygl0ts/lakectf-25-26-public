import random
N_STATES = 10
N_INPUTS = 8

random.seed(42)
final_state = N_STATES - 1
transitions =[]
for s in range(N_STATES):
    transitions.append([0]*N_INPUTS)
    for i in range(N_INPUTS):
        r = random.randint(0, 3)
        next_state = 0
        if (r == 0): 
            next_state = s
        if (r == 1): 
            next_state = min(s + 1, final_state)
        if (r == 2): 
            next_state = min(s + 2, final_state)
        if (r == 3): 
            next_state = max(s - 1, 0)

        transitions[s][i] = next_state

print(transitions)
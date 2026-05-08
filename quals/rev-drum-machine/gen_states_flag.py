import random
flag = "EPFL{dance_along_to_the_b34t_of_the_fl4g!}"
random.seed(42)
print(len(flag))

inputs = []
N_INPUTS = 8
for f in flag:
    # mask all bits from 0 to 7 and return them separately
    for i in range(N_INPUTS):
        if ((ord(f) >> i) & 1):
            print(i, end='')
    inputs.append([ (ord(f) >> i) & 1 for i in range(N_INPUTS) ])
# print(inputs)
final_state = 0
N_STATES = 182
transitions = [[0]*N_INPUTS for _ in range(N_STATES)]
s = 0
counter = [0]* N_INPUTS
a = 0
for c in inputs:
    # transitions.append([0]*N_INPUTS)
    for i in range(N_INPUTS):
        instrument = c[i]
        if instrument == 0:
            r = random.randint(0, 3)
            next_state = 0
            if (r == 0): 
                next_state = s
            if (r == 1): 
                next_state = s + 1
            if (r == 2): 
                next_state = s + 2
            if (r == 3): 
                next_state = s - 1
        else:
            next_state = s + 1
            final_state = next_state
            counter[i] += 1
            a += 1
        try:
            transitions[s][i] = next_state
        except:
            print(s)
            exit()
        s = next_state if instrument == 1 else s
        

print(transitions)
print(counter)
print("Final state:", final_state)
print(len(transitions))
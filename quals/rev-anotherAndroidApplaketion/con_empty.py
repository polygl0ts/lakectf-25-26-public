from z3 import *

flag = b"EPFL{Wh1_3v3n_b0th3r_w1th_J4v4_1n_th3_f1rst_Pl4c3?????}"

def do_check(input_length):
    # Create a Z3 solver instance
    solver = Solver()

    # Create a list of integer variables for the byte values
    byte_vars = [BitVec(f'byte_{i}', 8) for i in range(input_length)]
    # Add constraints for each variable to ensure they are in the range [0, 255]
    for byte in byte_vars:
        solver.add(byte >= 0, byte <= 127)

    # Add the constraint for the sum of the byte values

    even = [b for i, b in enumerate(byte_vars) if i%2==0]
    odd = [b for i, b in enumerate(byte_vars) if i%2==1]

    solver.add(byte_vars[0] == ord('E'))
    solver.add(byte_vars[1] == ord('P'))
    solver.add(byte_vars[2] == ord('F'))
    solver.add(byte_vars[3] == ord('L'))
    solver.add(byte_vars[4] == 123)
    solver.add(byte_vars[-1] == 125)
REPLACE

# Check if the constraints are satisfiable
    if solver.check() == sat:
        # Get a satisfying model
        model = solver.model()
        solution = [model[byte].as_long() for byte in byte_vars]
        return solution
    else:
        return None

result = do_check(len(flag))
if result:
    print(f"Solution found: {result}")
    print(f"Sum: {sum(result)}")
    out = "".join([chr(c) for c in result])
    print(out)
else:
    print("No solution exists.")


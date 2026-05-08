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
    solver.add(byte_vars[1] - byte_vars[43] - byte_vars[50] == -78)
    solver.add(byte_vars[6] + byte_vars[48] + byte_vars[42] == 271)
    solver.add(byte_vars[20] + byte_vars[31] + byte_vars[41] == 259)
    solver.add(byte_vars[8] - byte_vars[34] - byte_vars[21] == -140)
    solver.add(byte_vars[21] + byte_vars[17] + byte_vars[52] == 286)
    solver.add(byte_vars[16] - byte_vars[31] - byte_vars[11] == 16)
    solver.add(byte_vars[15] - byte_vars[31] - byte_vars[0] == -70)
    solver.add(byte_vars[33] + byte_vars[2] + byte_vars[43] == 260)
    solver.add(byte_vars[32] + byte_vars[13] + byte_vars[37] == 300)
    solver.add(byte_vars[33] - byte_vars[0] - byte_vars[51] == -37)
    solver.add(byte_vars[26] + byte_vars[45] + byte_vars[1] == 262)
    solver.add(byte_vars[50] - byte_vars[33] - byte_vars[12] == -142)
    solver.add(byte_vars[42] - byte_vars[13] - byte_vars[35] == -83)
    solver.add(byte_vars[8] - byte_vars[2] - byte_vars[40] == -89)
    solver.add(byte_vars[45] + byte_vars[29] + byte_vars[13] == 255)
    solver.add(byte_vars[31] - byte_vars[23] - byte_vars[32] == -177)
    solver.add(byte_vars[54] - byte_vars[9] - byte_vars[42] == -42)
    solver.add(byte_vars[12] + byte_vars[2] + byte_vars[16] == 296)
    solver.add(byte_vars[2] + byte_vars[16] + byte_vars[9] == 237)
    solver.add(byte_vars[22] - byte_vars[6] - byte_vars[54] == -180)
    solver.add(byte_vars[12] + byte_vars[15] + byte_vars[14] == 256)
    solver.add(byte_vars[15] + byte_vars[41] + byte_vars[39] == 212)
    solver.add(byte_vars[5] - byte_vars[45] - byte_vars[14] == -119)
    solver.add(byte_vars[11] + byte_vars[29] + byte_vars[16] == 219)
    solver.add(byte_vars[47] + byte_vars[19] + byte_vars[50] == 276)
    solver.add(byte_vars[25] + byte_vars[44] + byte_vars[32] == 285)
    solver.add(byte_vars[2] - byte_vars[31] - byte_vars[52] == -42)
    solver.add(byte_vars[36] - byte_vars[7] - byte_vars[31] == -47)
    solver.add(byte_vars[21] - byte_vars[50] - byte_vars[7] == 7)
    solver.add(byte_vars[46] + byte_vars[47] + byte_vars[17] == 255)
    solver.add(byte_vars[44] - byte_vars[24] - byte_vars[0] == -93)
    solver.add(byte_vars[7] + byte_vars[6] + byte_vars[44] == 233)
    solver.add(byte_vars[45] - byte_vars[16] - byte_vars[22] == -57)
    solver.add(byte_vars[35] + byte_vars[6] + byte_vars[3] == 284)
    solver.add(byte_vars[27] + byte_vars[36] + byte_vars[8] == 198)
    solver.add(byte_vars[16] + byte_vars[53] + byte_vars[44] == 259)
    solver.add(byte_vars[22] + byte_vars[8] + byte_vars[9] == 195)
    solver.add(byte_vars[34] + byte_vars[6] + byte_vars[28] == 338)
    solver.add(byte_vars[26] + byte_vars[36] + byte_vars[49] == 188)
    solver.add(byte_vars[14] - byte_vars[20] - byte_vars[53] == -60)
    solver.add(byte_vars[38] + byte_vars[32] + byte_vars[16] == 328)
    solver.add(byte_vars[2] - byte_vars[24] - byte_vars[25] == -129)
    solver.add(byte_vars[13] - byte_vars[42] - byte_vars[35] == -125)
    solver.add(byte_vars[54] + byte_vars[8] + byte_vars[27] == 272)
    solver.add(byte_vars[20] - byte_vars[22] - byte_vars[18] == -5)
    solver.add(byte_vars[27] - byte_vars[30] - byte_vars[46] == -95)
    solver.add(byte_vars[33] - byte_vars[14] - byte_vars[42] == -119)
    solver.add(byte_vars[16] + byte_vars[37] + byte_vars[0] == 280)
    solver.add(byte_vars[17] - byte_vars[12] - byte_vars[18] == -57)
    solver.add(byte_vars[29] + byte_vars[22] + byte_vars[33] == 196)
    solver.add(byte_vars[14] + byte_vars[5] + byte_vars[34] == 301)
    solver.add(byte_vars[40] + byte_vars[10] + byte_vars[11] == 283)
    solver.add(byte_vars[31] - byte_vars[39] - byte_vars[13] == -95)
    solver.add(byte_vars[9] + byte_vars[25] + byte_vars[18] == 197)
    solver.add(byte_vars[42] - byte_vars[7] - byte_vars[49] == 4)
    solver.add(byte_vars[54] - byte_vars[28] - byte_vars[20] == -88)
    solver.add(byte_vars[10] - byte_vars[48] - byte_vars[2] == -3)
    solver.add(byte_vars[25] - byte_vars[39] - byte_vars[28] == -72)
    solver.add(byte_vars[47] - byte_vars[29] - byte_vars[4] == -76)
    solver.add(byte_vars[16] - byte_vars[52] - byte_vars[26] == -21)
    solver.add(byte_vars[54] - byte_vars[21] - byte_vars[26] == -68)
    solver.add(byte_vars[37] + byte_vars[52] + byte_vars[25] == 253)
    solver.add(byte_vars[21] + byte_vars[26] + byte_vars[2] == 263)
    solver.add(byte_vars[7] - byte_vars[19] - byte_vars[21] == -184)
    solver.add(byte_vars[50] + byte_vars[3] + byte_vars[21] == 258)
    solver.add(byte_vars[46] + byte_vars[14] + byte_vars[25] == 245)
    solver.add(byte_vars[49] + byte_vars[19] + byte_vars[40] == 291)
    solver.add(byte_vars[20] - byte_vars[2] - byte_vars[4] == -98)
    solver.add(byte_vars[25] - byte_vars[27] - byte_vars[36] == -8)
    solver.add(byte_vars[27] + byte_vars[32] + byte_vars[23] == 278)
    solver.add(byte_vars[52] + byte_vars[9] + byte_vars[47] == 213)
    solver.add(byte_vars[38] + byte_vars[5] + byte_vars[32] == 299)
    solver.add(byte_vars[2] - byte_vars[0] - byte_vars[37] == -94)
    solver.add(byte_vars[31] + byte_vars[39] + byte_vars[24] == 202)
    solver.add(byte_vars[24] - byte_vars[51] - byte_vars[47] == -58)
    solver.add(byte_vars[15] + byte_vars[25] + byte_vars[5] == 230)
    solver.add(byte_vars[39] + byte_vars[20] + byte_vars[18] == 195)
    solver.add(byte_vars[7] - byte_vars[14] - byte_vars[23] == -165)
    solver.add(byte_vars[28] + byte_vars[31] + byte_vars[30] == 262)
    solver.add(byte_vars[9] + byte_vars[12] + byte_vars[21] == 280)

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


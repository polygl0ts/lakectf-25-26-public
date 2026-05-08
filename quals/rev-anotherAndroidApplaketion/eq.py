import random
import os
import copy
import hashlib
import secrets

flag = b"EPFL{Wh1_3v3n_b0th3r_w1th_J4v4_1n_th3_f1rst_Pl4c3?????}"

random.seed(420)

check_classes = list(range(0,99))
check_methods = list(range(0,99))

correct_seq = []

z3_eq = []
NR_CHECKS = 80
def sha(s):
    s = str(s)
    hash_object = hashlib.sha256(s.encode())
    return hash_object.hexdigest()

def generate_java_class(class_name, valid_checks):
    out = f"""package com.lake.ctf;

public class Check{sha(class_name)} {{
    public static native void nop(String a, String b);
    static {{
        System.loadLibrary("ohgreat2");
    }}
"""

    java_valid_checks = []
    valid_methods = []
    for meth, check_info, next_c, next_m in valid_checks:
        idx1, idx2, idx3, operator, sol = check_info 
        check = f"""
        static boolean Check{sha(meth)}(String wow) {{
            if((int)wow.charAt({idx1}) {operator} (int)wow.charAt({idx2}) {operator} (int)wow.charAt({idx3}) == {sol}){{
                nop("{sha(next_c)}", "{sha(next_m)}");
                return true;
            }} else {{
                nop("{sha(random.choice(check_classes))}", "{sha(random.choice(check_methods))}");
                return false;
            }}
        }}"""
        java_valid_checks.append(check)
        valid_methods.append(meth)
   
    fake_methods = [] 
    for meth in check_methods:
        if meth in valid_methods: continue
        idx1, idx2, idx3, operator, sol = generate_random_equation(flag, valid=False)
        check = f"""
        static boolean Check{sha(meth)}(String wow) {{
            if((int)wow.charAt({idx1}) {operator} (int)wow.charAt({idx2}) {operator} (int)wow.charAt({idx3}) == {sol}){{
                nop("{sha(random.choice(check_classes))}", "{sha(random.choice(check_methods))}");
                return true;
            }} else {{
                nop("{sha(random.choice(check_classes))}", "{sha(random.choice(check_methods))}");
                return false;
            }}
        }}"""
        fake_methods.append(check)
    
    all_checks = fake_methods + java_valid_checks 
    random.shuffle(all_checks)
    out += '\n'.join(all_checks)
 
    out += "\n}"
    open(f'hello-libs/app/src/main/java/com/lake/ctf/Check{sha(class_name)}.java','w+').write(out)

def generate_random_equation(byte_vars, valid):
    """
    Generates a random equation involving two randomly indexed bytes from the input byte string.
    The equation is formatted for inclusion in a Z3 script.
    """
    # Ensure input is bytes
    if not isinstance(byte_vars, (bytes, bytearray)):
        raise ValueError("Input must be a bytes-like object.")
    
    # Get the length of the byte string
    length = len(byte_vars)
    
    # Randomly pick two distinct indices
    idx1, idx2, idx3 = random.sample(range(length), 3)
    
    # Randomly select an operator
    operator = random.choice(['+', '-'])
    if valid:
        sol = eval(f'{byte_vars[idx1]} {operator} {byte_vars[idx2]} {operator} {byte_vars[idx3]}')
    else:
        sol2 = eval(f'{byte_vars[idx1]} {operator} {byte_vars[idx2]} {operator} {byte_vars[idx3]}')
        while True:
            if operator == '+':
                sol = random.choice(list(range(96,379)))
            elif operator == '-':
                sol = random.choice(list(range(-220 ,63)))
            elif operator == '^':
                sol = random.choice(list(range(0x20, 0x7e)))
            else:
                print("????")
                exit(-1)
            if sol!= sol2:
                break
    if valid:
        # Construct the Z3 equation
        z3_eq.append(f"    solver.add(byte_vars[{idx1}] {operator} byte_vars[{idx2}] {operator} byte_vars[{idx3}] == {sol})")

    return idx1, idx2, idx3, operator, sol

def get_class_checks(valid_checks, classs):
    out = []
    for i, data in enumerate(valid_checks):
        c_c, c_m, c_i = data
        if c_c == classs:
            if i+1 < len(valid_checks):
               next_c, next_m, _ = valid_checks[i+1]
            else:
                next_c = random.choice(check_classes)
                next_m = random.choice(check_methods)
            out.append((c_m, c_i, next_c, next_m))
    return out

def update_hello_libs(valid_check):
    a = open('hello-libs.cpp').read()
    a = a.replace("REPLACE1", sha(valid_check[0]))
    a = a.replace("REPLACE2", sha(valid_check[1]))
    registrations = "jclass c;\n"
    for c in check_classes:
        registrations += f"c = env->FindClass(\"com/lake/ctf/Check{sha(c)}\");\n"
        registrations += f"env->RegisterNatives(c, (const JNINativeMethod *)&buf, 1);" 
    a = a.replace("REPLACE3", registrations)
    open("hello-libs/app/src/main/cpp/hello-libs.cpp", "w+").write(a)      
 
def update_main():
    """
    boolean r1 = Test(maybe_flag);
                boolean r2 = Test(maybe_flag);
                if(r1 && r2) {
                    textView.setText("flag is correct!");
    """
    out = ""
    for i in range(0, NR_CHECKS):
        out += f"boolean r{i} = Test(maybe_flag);\n"
    out += "if("
    for i in range(0, NR_CHECKS):
        out += f"r{i} &&"
    out += "true) {\n"
    out += "textView.setText(\"flag correct!\");\n" 

    a = open("MainActivity.java").read()
    a = a.replace("REPLACE2", str(len(flag)))
    a = a.replace("REPLACE", out)
    open("hello-libs/app/src/main/java/com/lake/ctf/MainActivity.java", "w+").write(a)

os.system("rm hello-libs/app/src/main/java/com/lake/ctf/*java")
os.system("rm hello-libs/app/src/main/cpp/hello-libs.cpp") 

valid_checks = []
chosen_checks = []
for _ in range(0, NR_CHECKS):
    check_info = generate_random_equation(flag, valid=True)
    while 1:
        chosen_class = random.choice(check_classes)
        chosen_meth = random.choice(check_methods)
        if (chosen_class,chosen_meth) not in chosen_checks:
            chosen_checks.append((chosen_class, chosen_meth))
            break
    print("adding check", chosen_class, chosen_meth)
    correct_seq.append(f'{sha(chosen_class)} {sha(chosen_meth)}')
    valid_checks.append((chosen_class, chosen_meth, check_info))
    

for classs in check_classes:
    checks = get_class_checks(valid_checks, classs)
    print("generating class", classs)
    generate_java_class(classs, checks)


# update initial class
update_hello_libs(valid_checks[0])
update_main()

con = open("con_empty.py").read()
con = con.replace("REPLACE", "\n".join(z3_eq))
print(con.encode())
open("con.py","w").write(con)

open("seq.txt","w").write("\n".join(correct_seq))

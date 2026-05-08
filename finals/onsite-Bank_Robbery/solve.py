charset=["A", "B", "C", "D", "*", "#", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

import hashlib

se = "87*D5#"
res = hashlib.md5(se.encode())

for a in charset:
    for b in charset:
        for c in charset:
            for d in charset:
                for e in charset:
                    for f in charset:
                        st= a + b + c+ d +e + f    
                        attempt = hashlib.md5(st.encode())
                        if(attempt.hexdigest() == res.hexdigest()):
                            print(attempt.hexdigest())
                            print(res.hexdigest())
                            print(st) 

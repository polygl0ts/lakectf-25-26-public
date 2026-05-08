#!/usr/bin/env python3
import subprocess
import base64
import tempfile
import os

obj_dump_orig = subprocess.check_output(["objdump", "-d", "-f", "silent-lake"])
obj_dump_orig = obj_dump_orig.decode("utf-8")
based_binary = input("Enter the base64 encoded binary: ")
binary = base64.b64decode(based_binary)
with tempfile.NamedTemporaryFile(delete=False) as f:
    f.write(binary)
    f.flush()
    name = f.name
try:
    obj_dump_new = subprocess.check_output(["objdump", "-d", "-f", name])
    obj_dump_new = obj_dump_new.decode("utf-8")
    obj_dump_new = obj_dump_new.replace(name, "silent-lake")
    if (obj_dump_orig == obj_dump_new):
        os.chmod(name, 0o755)
        res = subprocess.check_output([name, "asdf"])
        print(res)
except:
    pass
finally:
    os.unlink(name)

import sys

def main():
    fname = sys.argv[1]
    outfname = sys.argv[2]

    with open(outfname, "w") as fout:
        fout.write("char arr[] = {")
        with open(fname) as fin:
            data = fin.read()
            fout.write(f"{ord(data[0])}")
            for c in data[1:]:
                fout.write(f",{ord(c)}")
        fout.write("};")


if __name__ == "__main__":
    main()

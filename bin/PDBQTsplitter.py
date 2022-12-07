#! /usr/bin/env python3

import argparse
import threading
import gzip


def read_pdbqt(fname):

    if fname.endswith("pdbqt.gz"):
        with gzip.open(fname, "r") as pdbqt:
            flines = pdbqt.read()
            
    elif fname.endswith(".pdbqt"):
        with open(fname, "r") as pdbqt: 
            flines = pdbqt.readlines()
    else:
        print("Oops, your downloaded ligand file is not in .pdbqt format")            
        pass
        
    return flines

        
def write_pdbqt(file_name, input_array):
    with open(file_name, "a") as outfile:
        for x in input_array:
            outfile.write(x)
    return None



def split_pdbqt(fname, out_path):
    infile = read_pdbqt(fname)
    atoms_array = []
    check_name = []
    fname = ""

    for i in range(len(infile)):
        line = infile[i]
        if "MODEL " in line:
            fname = infile[i + 1].split("=")[1].strip("\n")
            fname = fname.strip(" ")
            atoms_array = []
        elif "ENDMDL" not in line:
            atoms_array.append(line)
        else:
            continue

        if "ENDMDL" in infile[i + 1]:
            if fname not in check_name:
                if out_path[-1] != "/":
                    outfname = "{0}/{1}.pdbqt".format(out_path, fname)
                else:
                    outfname = "{0}{1}.pdbqt".format(out_path, fname)
                print(fname, atoms_array)
                write_pdbqt(file_name=outfname, input_array=atoms_array)
                check_name.append(fname)
    
    return None


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("-i", "--input", help="[REQUIRED] Input path multi-PDBQT directory", required=True)
    args.add_argument("-o", "--out", help="[REQUIRED] Output path for individual .PDBQT files", required=True)
    parser = args.parse_args()
    split_pdbqt(parser.input, parser.out)


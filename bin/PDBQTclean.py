#! /usr/bin/env python3

""" 
PDBQTclean.py - a program to clean input PDBQT files that may contain duplicate coordinates.

Clean PDBQT files ready for docking with programs such as AutoDock4 or AutoDock Vina.

Note:  Sometimes, files downloaded from ZINC will contain duplicates. Our default docking algorithm, Qvina2, can handle ligand files with
duplicates, but other algorithms such as AutoDock Vina cannot. We provide this script to do post-cleaning of ligand PDBQT files after
using the Splitter.py program.

"""

import os
import pathlib
import argparse
import multiprocessing



def read_pdbqt(file_path):
    file_path = pathlib.Path(file_path)
    if file_path.suffix == ".pdbqt":
        with file_path.open("r") as pdbqt:
            lines = pdbqt.readlines()
    else:
        raise ValueError("Oops, your downloaded ligand file is not in .pdbqt format")
    return lines



def write_pdbqt(file_path, out_path, lines):
    output_file_path = pathlib.Path(out_path) / file_path.name
    with output_file_path.open("w") as file:
        file.writelines(lines)
    print(f"Cleaning complete. Ligand file written to: {output_file_path}")



def clean_pdbqt(file_path, out_path):
    lines = []
    file_lines = read_pdbqt(file_path)
    start = False
    for line in file_lines:
        if line.startswith("REMARK  Name"):
            start = True
        if start:
            lines.append(line)
        if line.startswith("TORSDOF"):
            break
    write_pdbqt(file_path, out_path, lines)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="[REQUIRED] Input path to split .PDBQT directory", required=True)
    parser.add_argument("-o", "--out", help="[REQUIRED] Output path for refined .PDBQT files", required=True)
    args = parser.parse_args()

    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.out)

    if not input_path.is_dir():
        raise ValueError("Input path is not a valid directory")
    if not output_path.is_dir():
        raise ValueError("Output path is not a valid directory")

    ligands = os.listdir(input_path)

    with multiprocessing.Pool() as pool:
        results = []
        for ligand_file in ligands:
            ligand_file_path = input_path / ligand_file
            result = pool.apply_async(clean_pdbqt, (ligand_file_path, output_path))
            results.append(result)

        # Wait for all tasks to complete
        for result in results:
            result.get()

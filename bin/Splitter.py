#! /usr/bin/env python3

import argparse
import os
import threading



def PDBQT_splitter(input_dir_path, output_dir_path):
    input_list = os.listdir(input_dir_path)
    
    for file in input_list:
        input_path = "{0}/{1}".format(input_dir_path, file)
        print(input_path)
        split_cmd = "PDBQTsplitter -i {0} -o {1}".format(input_path, output_dir_path)
        os.system(split_cmd) 
     
    return None



if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('-i', '--input_dir', help="[REQUIRED] Path to multi-PDBQT file folder", required=True)
    args.add_argument('-o', '--out_dir', help="[REQUIRED] Path to output folder", required=True)
    paser = args.parse_args()

    PDBQT_splitter(input_dir_path=paser.input_dir, output_dir_path=paser.out_dir)

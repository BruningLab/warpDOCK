#! /usr/bin/env python3

import pandas as pd
import os
import argparse



def ReDocking(pdbqtfiles, csvfile, newfolder, top):
    df_csv = pd.read_csv(csvfile).sort_values("Max")
    top_select = df_csv[0:int(top)]['Ligand'].tolist()

    for i in top_select:
        cp_cmd = "cp {0}/{1} {2}".format(os.path.abspath(pdbqtfiles), i, os.path.abspath(newfolder))
        print("Copying : {0}".format(i))
        os.system(cp_cmd)
        
    return None



if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("-i", "--pdbqtfiles", help="Path to the PDBQT file library folder", required=True)
    args.add_argument("-c", "--csv", help="Path to the CSV file containing summarised docking results", required=True)
    args.add_argument("-n", "--newfolder", help="Path to the new folder", required=True)
    args.add_argument("-t", "--top", help="Top selection e.g., 100", required=True, type=int)
    paser = args.parse_args()
    ReDocking(pdbqtfiles=paser.pdbqtfiles, csvfile=paser.csv, newfolder=paser.newfolder, top=paser.top)

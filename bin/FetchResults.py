#!/usr/bin/env python3

import os
import argparse
import csv
import threading



def get_affinity(inline):
    rt_affi = ""
    max_affi = inline.split(" ")
    for affi in max_affi:
        if "-" in affi:
            rt_affi = affi
        else:
            continue
    return rt_affi



def get_affinity_list(logpath, nump, out):   
    max_affinity = []
    min_affinity = []
    molfiles = []
    
    split_outf = out.split(".")
    if split_outf[-1] == "csv":
        out = out
    else:
        out = "{0}.csv".format(out)       
        print("!WARNING: Resulting file must be a 'csv' file. Therefore, the file extension updated")


    if logpath[-1] == "/":
        logpath = logpath
    else:
        logpath = "{0}/".format(logpath)

    flist = os.listdir(logpath)
    
    for fname in flist:
        print("Reading file {} ".format(fname))
        fpath = "{0}{1}".format(logpath, fname)
        
        with open(fpath, "r") as fin:
            for i in fin:
                if "   1      " in i:
                    maxa = get_affinity(inline=i)
                    max_affinity.append(maxa)
                    molfiles.append(fname)

                if "   {0}       ".format(nump) in i:
                    mina = get_affinity(inline=i)
                    min_affinity.append(mina)


    rows = zip(molfiles, max_affinity, min_affinity)
    header = ["Ligand", "Max", "Min"]
    
    with open(out, "w") as file:
        
        writer = csv.writer(file)
        writer.writerow(i for i in header)
        for row in rows:
            writer.writerow(row)
            
            
        
if __name__ == '__main__':
    args = argparse.ArgumentParser(description="Fetch Results")
    args.add_argument("-logpath", help="[REQUIRED] Path to the log file folder", required=True, type=str)
    args.add_argument("-nump", help="[REQUIRED] Number of docking poses", required=True, type=int)
    args.add_argument("-out", help="[REQUIRED] Output CSV file name (*.csv)", required=True, type=str)
    paser = args.parse_args()

    get_affinity_list(logpath=paser.logpath, nump=paser.nump, out=paser.out)


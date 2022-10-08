#!/usr/bin/env python3

import os
import argparse
import threading



def get_ip_List(ip_list):
    with open(ip_list, "r") as my_ip:
        ip_in = my_ip.read()
        ip_array = ip_in.split()
        return ip_array



def file_mover(fpath, ips):
    flist = os.listdir(os.path.abspath(fpath))
    n_iplist = len(get_ip_List(ip_list=ips))

    for i in range(n_iplist):
        mkdir = "mkdir {0}".format(str(i))
        os.system(mkdir)
    split = n_iplist
    split_length = int(len(flist)/split)

    counter = 0
    start = 0
    while counter < split:
        if start == 0:
            copying_file_list = flist[start:start + split_length]
        elif counter == split-1:
            copying_file_list = flist[start:len(flist)]
        else:
            copying_file_list = flist[start:start + split_length]
        start = start + split_length
        
        for file in copying_file_list:
            source = "{0}/{1}".format(os.path.abspath(fpath), file)
            destination = "{0}/{1}".format(os.path.abspath(os.getcwd()), str(counter))
            mv_cmd = "cp {0} {1}".format(source, destination)
            print("Now copying : ", mv_cmd)
            os.system(mv_cmd)
        counter += 1



if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("-input", help="Path to PDBQT file library for splitting into instance batches", required=True, type=str)
    args.add_argument("-ips", help="Path to the IP list file", required=True, type=str)
    paser = args.parse_args()
    file_mover(fpath=paser.input, ips=paser.ips)


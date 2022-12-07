#!/usr/bin/env python3

import subprocess
import time
import threading
import os
import argparse



def get_ip_List(ip_list):
    with open(ip_list, "r") as my_ip:
        ip_in = my_ip.read()
        ip_array = ip_in.split()
        return ip_array



def run(key, user, ip, command):
    computer = "{0}@{1}".format(user, ip)
    cmd = ["ssh", "-i", key, "-t", computer, command]
    process = subprocess.Popen(cmd)
    process.communicate()
    return None



if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("-key", help="Path to the private key", required=True)
    args.add_argument("-path", help="Path to the directory with pre-partitioned libraries", required=True)
    args.add_argument("-ips", help="Path to the IP address file", required=True)
    args.add_argument("-results", help="Path to results output folder", required=True)
    args.add_argument("-logs", help="Path to logs output folder", required=True)
    args.add_argument("-receptor", help="Path to receptor.pdbqt file", required=True)
    args.add_argument("-config", help="Path to configuration file", required=True)
    args.add_argument("-sfactor", help="Scaling factor (1 to 4)", required=True)
    parser = args.parse_args()

    if parser.path[-1] == "/":
        path = parser.path
    else:
        path = "{0}/".format(parser.path)

    iplist = get_ip_List(ip_list=parser.ips)
    
    for ip in iplist:
        pre_command = "WarpDrive " \
                      "-results {1}/ " \
                      "-logs {2}/ " \
                      "-receptor {3} " \
                      "-config {4} " \
                      "-sfactor {5}".format(path, parser.results, parser.logs, parser.receptor, parser.config, parser.sfactor)


        run_command = "{0} -pdbqt {1}/{2}".format(pre_command, parser.path, iplist.index(ip))
        print("Running on {0}".format(ip))
        
        threading.Thread(target=run, args=[os.path.abspath(parser.key), "ubuntu", ip, run_command]).start()
        print(run_command)
        
        time.sleep(1)


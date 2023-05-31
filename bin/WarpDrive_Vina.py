#!/usr/bin/env python3

""" 
AutoDock Vina specific queue-engine

The main difference to Qvina2/W is that Vina does not support LOG output.

"""


import subprocess
import argparse
import multiprocessing
import time
import datetime
import sys
import os



def process_monitor(delay):
    vina_count = int()
    cmd = ['ps', '-ef']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    pout = process.communicate()
    for i in pout:
        try:
            p = i.decode()
            if "vina " in p:
                vina_count = p.count('vina ')
        except AttributeError:
            continue
    time.sleep(delay)
    return vina_count



def pg_bar(array_length, counter, process_count):
    percentage = round((float(counter) / array_length) * 100, 2)
    pg = "|" * int(percentage)
    space = "-" * (100 - len(pg))
    bar = "\rP={3}  0% [{0}{1}] 100%   Your progress: {2}%".format(pg, space, percentage, process_count)
    sys.stdout.write(bar)
    sys.stdout.flush()
    return None



def load_process(inputfile_path, result_file_path, receptor_path, vina_config):
    cmd = "vina --config {0} --ligand {1} --out {2} --receptor {3}". \
        format(vina_config, inputfile_path, result_file_path, receptor_path)
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return None
  
  
  
def driver(pdbqt_path, results_path, receptor_path, vina_config, show_queue=False, scaling_factor=1, delay=0):
    counter = 0
    file_list = os.listdir(pdbqt_path)
    num_cpus = multiprocessing.cpu_count()
    while counter < len(file_list):
        infile = file_list[counter]
        if show_queue == 'y' or show_queue == 'Y':
            print("Next in the queue: ", infile)

        # Get input file and path
        if pdbqt_path[-1] == "/":
            infile_path = "{0}{1}".format(pdbqt_path, infile)
        else:
            infile_path = "{0}/{1}".format(pdbqt_path, infile)

        # Set output file and path
        if results_path[-1] == "/":
            result_file_path = "{0}{1}".format(results_path, infile)
        else:
            result_file_path = "{0}/{1}".format(results_path, infile)

        # Process monitor function
        running_processes = process_monitor(delay=delay)

        if running_processes <= (num_cpus * scaling_factor):
            if show_queue == 'y' or show_queue == 'Y':
                print("Current number of threads: ", running_processes / 2, " >> loading ---> ", infile)

            # Load process function
            load_process(inputfile_path=infile_path, result_file_path=result_file_path,
                         vina_config=vina_config, receptor_path=receptor_path)
            counter += 1
        else:
            time.sleep(1)

        # Progress bar
        if show_queue == 'n' or show_queue == 'N':
            pg_bar(array_length=len(file_list), counter=counter, process_count=running_processes)

    return None
  
  
  
if __name__ == '__main__':


    args = argparse.ArgumentParser(description="WarpDrive Queue Engine")
    args.add_argument('-pdbqt', help="[REQUIRED] Path to the PDBQT instance batches folder", required=True, type=str)
    args.add_argument('-results', help="[REQUIRED] Path to the results output folder", required=True, type=str)
    args.add_argument('-receptor', help="[REQUIRED] Path to the receptor file", required=True, type=str)
    args.add_argument('-config', help="[REQUIRED] Path to Vina config file", required=True, type=str)
    args.add_argument('-squeue', help="[OPTIONAL] Show queuing process (default=N)", required=False, type=str,
                      default='N', choices=['Y', 'N'])
    args.add_argument('-sfactor', help="[OPTIONAL] CPU scaling factor (default = 1)", required=False, type=int,
                      default=1, choices=[1,2,3,4])
    args.add_argument('-delay', help="[OPTIONAL] Delay for loading the next process (default=0)", required=False,
                      type=float, default=0)
    args.add_argument('-args', help="[DIAGNOSTIC] print input arguments (default=N)", required=False, type=str,
                      default='N', choices=['Y', 'N'])
    paser = args.parse_args()

    pdbqt_path = paser.pdbqt
    results = paser.results
    receptor_path = paser.receptor
    vina_config = paser.config
    show_queue = paser.squeue
    scaling_factor = paser.sfactor
    delay = paser.delay
    p_args = paser.args
    if p_args == "y" or p_args == "Y":
        print(paser)
        exit()

    start = time.time()
    driver(pdbqt_path=pdbqt_path, results_path=results, receptor_path=receptor_path,
           vina_config=vina_config, show_queue=show_queue, scaling_factor=scaling_factor, delay=delay)
    print("     Running the last batch ...")

    while True:
        if process_monitor(delay=1) == 0:
            break

    end = time.time()
    time_taken = int(end - start)
    complete_msg = "\nQueue completed in {0} ".format(datetime.timedelta(seconds=time_taken))
    print(complete_msg)
  

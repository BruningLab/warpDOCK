#! /usr/bin/env python3

import argparse
import os
import sys


def get_urls(furl):
    with open(furl, "r") as urlf:
        urls = urlf.readlines()
    return urls


def pg_bar(array_length, saving_path):
    counter = len(os.listdir(saving_path))
    percentage = round((float(counter) / array_length) * 100, 2)
    pg = "|" * int(percentage)
    space = "-" * (100 - len(pg))
    bar = "\r  0% [{0}{1}] 100%   Your progress: {2}%\n".format(pg, space, percentage)
    sys.stdout.write(bar)
    sys.stdout.flush()
    return None


def downloader(furl, saving_path):
    abs_saving_path = os.path.abspath(saving_path)
    for i in get_urls(furl):
        cmd = "wget {0} -P {1}".format(i.strip("\n"), abs_saving_path)
        os.system(cmd)
        gfname = i.split("/")[-1].strip("\n")
        cmd_gzip = "gzip -d {0}{1}".format(abs_saving_path, gfname)
        os.system(cmd_gzip)

        pg_bar(array_length=len(get_urls(furl)), saving_path=abs_saving_path)
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download ZINC URLs")
    parser.add_argument("-i", "--input", help="[REQUIRED] Input file with urls", required=True)
    parser.add_argument("-o", "--out", help="[REQUIRED] Output folder path", required=True)
    args = parser.parse_args()
    downloader(furl=args.input, saving_path=args.out)

import argparse
import os

parser = argparse.ArgumentParser(description="check result fmt", prog="crf")
parser.add_argument("-d", "--dir", help="dir", required=True)
args = parser.parse_args()

dir_name = args.dir

for d in os.listdir(dir_name):
    fd = os.path.join(dir_name, d)
    if not os.path.isdir(fd):
        continue
    fd = os.path.join(dir_name, d, "results")
    if not os.path.isdir(fd):
        continue
    if len(list(os.listdir(fd))) != 1:
        print("Dir may have problem: %s", fd)
        exit(1)

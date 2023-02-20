# Test python list arguments using argparse

## To test it, run the following.
## python multiple_args.py 1 2 3 4

import argparse

parser = argparse.ArgumentParser()
## *: any number of arguments
## +: 1 or more arguments
parser.add_argument('nums', nargs='+')

args = parser.parse_args()

print("~ Nums: {}".format(args.nums))

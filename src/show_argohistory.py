#!/usr/bin/env python
# -*coding: UTF-8 -*-
__author__ = 'guillaumemaze'

import sys
import numpy as np
import xarray as xr
import pandas as pd
sys.path.append('/Users/gmaze/work/Projects/Oceans_Big_Data_Mining/ML_argoqc/python/src')
import pyargo as argo

# print "This is the name of the script: ", sys.argv[0]
# print "Number of arguments: ", len(sys.argv)
# print "The arguments are: " , str(sys.argv)
# print "2nd argument is: " , str(sys.argv[1])

import argparse
parser = argparse.ArgumentParser(description='Print Argo profile HISTORY')
parser.add_argument('ncfile', metavar='ncfile', type=str, nargs=1, help='Netcdf file to scan')
# parser.add_argument("--file", "-f", type=str, help='Netcdf file to scan', required=True)
args = parser.parse_args()
# print(args.accumulate(args.integers))

ds = xr.open_dataset(sys.argv[1])
for i_prof in ds['N_PROF']:
    argo.history.print_history(ds, int(i_prof.values))
    print "\n"
ds.close()
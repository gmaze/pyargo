# -*coding: UTF-8 -*-
#
# Provide useful methods to work with index files
#
__author__ = 'guillaumemaze'

import os
import pandas as pd
import numpy as np
import multiprocessing
from functools import partial

def read(index_file):
    """
        Read the Argo detailed index txt file and return it as a Panda Dataframe
    """
    return pd.read_csv(index_file,
                       sep=',', index_col=None, header=0, skiprows=8,
                       parse_dates=[1, 7, 13, 14],
                       dtype={'latitude': np.float32, 'longitude': np.float32,
                              'profiler_type': np.str,
                              'profile_temp_qc': np.str, 'profile_psal_qc': np.str, 'profile_doxy_qc': np.str,
                              'ad_psal_adjustment_mean': np.float32, 'ad_psal_adjustment_deviation': np.float32,
                              'n_levels': np.int})

def load(droot, ifile="argo_profile_detailled_index.txt", verb=False, cache=True, cachedir='.'):
    """
        Load an Argo detailed index file
        If read for the first time, a copy of the index is saved locally as a hdf5 file from
        which it is loaded on new calls much faster.
    """
    pre, ext = os.path.splitext(ifile)
    index = os.path.expanduser(os.path.join(droot, ifile))

    p = os.path.join(droot, pre)
    p = os.path.normcase(p)
    p = p.replace(os.path.sep, '')
    p = p.replace('-', '')
    p = p.replace('_', '')
    store = os.path.join(cachedir, p + '.h5')

    if cache:
        # Try to load the index from cache, or compute/save it if not found
        if os.path.isfile(store):
            if verb:
                print ("Loading cached Argo index file:\n%s") % (store)
            ai = pd.read_hdf(store, 'index')
        else:
            if verb:
                print ("Loading and Caching Argo index file:\n%s") % (index)
            ai = read(index)
            ai.to_hdf(store, 'index')
    else:
        if verb:
            print ("Loading Argo index file:\n%s") % (index)
        ai = read(index)
    return ai

def par_traverse(ai, rowfunc, num_cores='ncpu'):
    """"Apply a function on each of the Argo index rows, in parallel"""
    if num_cores=='ncpu':
        num_cores = multiprocessing.cpu_count()
    num_partitions = num_cores #number of partitions to split dataframe
    ai_split = np.array_split(ai, num_partitions)

    def parfun(func, d):
        """Function to apply "rowfunc" onto each of rows in a chunk d of Argo mono-profile files"""
        for index, row in d.iterrows():
            d.ix[index] = func(row)
        return d
    chunkfunc = partial(parfun, rowfunc)

    pool = multiprocessing.Pool(num_cores)
    results = pool.map(chunkfunc, ai_split)
    ai = pd.concat(results)
    pool.close()
    pool.join()
    return ai
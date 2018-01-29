# -*coding: UTF-8 -*-
__author__ = 'guillaumemaze'

import numpy as np
import xarray as xr
import pandas as pd
import sys
from . import reftable as ref
import warnings

def decodeqctest(qctest, hexa=False):
    """Identify the QC test numbers from a QCTEST value

        Examples from the Argo user manual page 117/118:
        with hexa=False (default):
            decodeqctest(434) = [1, 4, 5, 7, 8]
            decodeqctest(160) = [5, 7]
        with hexa=True:
            decodeqctest("1B2", hexa=True) = [1, 4, 5, 7, 8]
            decodeqctest("A0", hexa=True) = [5, 7]
    """
    if hexa:
        qctest = int(qctest, 16)

    powers = []
    ids = []
    i = 1
    while i <= qctest:
        if i & qctest:
            powers.append(i)
            ids.append(np.int(np.log2(i)))
        i <<= 1
    # return powers
    return ids

def delta_format(DT):
    sgn = '+'
    if DT<np.timedelta64(0):
        sgn = '-'
        DT=-DT
    days = DT.astype('timedelta64[D]').astype(np.int64) # gives: array([2, 2, 4, 2], dtype=int32)
    hours = DT.astype('timedelta64[h]').astype(np.int64)%24
    minutes = DT.astype('timedelta64[s]').astype(np.int64)%60
    # if days > 0 and hours > 0:
    #     return "{0:.0f} d, {1:.0f} h".format(days, hours)
    # elif days > 0:
    #     return "{0:.0f} d".format(days)
    # else:
    #     return "{0:.0f} h".format(hours)
    if days > 0 and hours > 0 and minutes > 0:
        return "{3}{0:.0f} Days {1:.0f}H{2:.2d}".format(days, hours, minutes, sgn)
    if hours > 0 and minutes > 0:
        return "{2}{0:.0f}H{1:.2d}".format(hours, minutes, sgn)
    elif hours > 0:
        return "{1}{0:.0f}H00".format(hours, sgn)
    else:
        return "{1}{0:.0f} Mins".format(minutes, sgn)

def delta_format(DT):
    sgn = '+'
    if DT<np.timedelta64(0):
        sgn = '-'
        DT=-DT
    # months = DT.astype('timedelta64[M]').astype(np.int64)
    # days = DT.astype('timedelta64[D]').astype(np.int64)
    # hours = DT.astype('timedelta64[h]').astype(np.int64)%24
    # minutes = DT.astype('timedelta64[s]').astype(np.int64)%60
    #
    # months = DT.astype('timedelta64[M]')
    # days = DT.astype('timedelta64[D]')
    # hours = DT.astype('timedelta64[h]')

    years = 0
    months = 0
    days = 0
    hours = 0
    minutes = np.timedelta64(DT, 'm').astype(np.float64)
    if minutes > 59:
        hours = np.timedelta64(DT, 'h').astype(np.float64)
        minutes = np.timedelta64(DT, 'm').astype(np.float64)%60
        if hours > 23:
            days = np.timedelta64(DT, 'D').astype(np.float64)
            hours = np.timedelta64(DT, 'h').astype(np.float64)%24
            if days > 30:
                days = np.timedelta64(DT, 'D').astype(np.float64)%30
                months = np.timedelta64(DT, 'D').astype(np.float64)/30
                if months > 11:
                    months = np.timedelta64(DT, 'D').astype(np.float64)/30%12
                    years = np.timedelta64(DT, 'D').astype(np.float64)/30/12

    if years >0 and months > 0 and days > 0 and hours > 0 and minutes > 0:
        S = "{3}{5:.0f} Years {4:.0f} Months {0:.0f} Days {1:.0f}H{2:2.0f}".format(days, hours, minutes, sgn, months, years)
    elif months >0 and days > 0 and hours > 0 and minutes > 0:
        S = "{3}{4:.0f} Months {0:.0f} Days {1:.0f}H{2:2.0f}".format(days, hours, minutes, sgn, months)
    elif days > 0 and hours > 0 and minutes > 0:
        S = "{3}{0:.0f} Days {1:.0f}H{2:2.0f}".format(days, hours, minutes, sgn)
    elif hours > 0 and minutes > 0:
        S = "{2}{0:.0f}H{1:2.0f}".format(hours, minutes, sgn)
    elif hours > 0:
        S = "{1}{0:.0f}H00".format(hours, sgn)
    else:
        S = "{1}{0:.0f} Mins".format(minutes, sgn)

    return S

def print_history(ds, i_prof, verb=0):
    """ Print the history of a profile from a xarray dataset"""
    def str_date(d):
        """Create our string representatiob of a numpy.datetime64 value"""
        return pd.to_datetime(str(d)).strftime('%Y-%m-%d %H:%M:%S')
    def cleanpstr(s):
        """Clean up a string contained in to a numpy array"""
        return s.astype(str).values.tostring().strip()

    def print_one_entry_old(ds, i_prof, nh):
        """Print data for one history entry"""
        msg = "%1s | %20s | %16s:\n"
        if nh==0:
            sys.stdout.write(msg % ('#', 'DATE', 'DATE vs CREATION'))

        HISTORY_DATE = np.datetime64(pd.to_datetime(ds['HISTORY_DATE'].sel(N_HISTORY=nh))[i_prof])  # YYYYMMDDHHMISS
        if nh > 0:
            HISTORY_DATE_prev = np.datetime64(pd.to_datetime(ds['HISTORY_DATE'].sel(N_HISTORY=nh - 1))[i_prof])
        DT = HISTORY_DATE - np.datetime64(pd.to_datetime(str(ds['DATE_CREATION'].values)))

        HISTORY_STEP = ds['HISTORY_STEP'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  # From Table 12
        HISTORY_ACTION = ds['HISTORY_ACTION'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  # From Table 7

        HISTORY_QCTEST_hex = ds['HISTORY_QCTEST'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  # From Table 11
        HISTORY_QCTEST_hex = HISTORY_QCTEST_hex.astype(str).values.tostring().strip()
        if not HISTORY_QCTEST_hex:
            HISTORY_QCTEST_int = '-'
            HISTORY_QCTEST_IDs = [0]
        else:
            try:
                HISTORY_QCTEST_int = int(HISTORY_QCTEST_hex, 16)
                HISTORY_QCTEST_IDs = decodeqctest(HISTORY_QCTEST_int)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise

        HISTORY_PARAMETER = ds['HISTORY_PARAMETER'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  # From Table 3
        HISTORY_START_PRES = ds['HISTORY_START_PRES'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  #
        HISTORY_STOP_PRES = ds['HISTORY_STOP_PRES'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  #
        HISTORY_PREVIOUS_VALUE = ds['HISTORY_PREVIOUS_VALUE'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  # Parameter/Flag previous value before action

        HISTORY_SOFTWARE = ds['HISTORY_SOFTWARE'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  #
        HISTORY_SOFTWARE_RELEASE = ds['HISTORY_SOFTWARE_RELEASE'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  #
        HISTORY_REFERENCE = ds['HISTORY_REFERENCE'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  #
        HISTORY_INSTITUTION = ds['HISTORY_INSTITUTION'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  # From Table 4

        # DT = HISTORY_DATE - ds['JULD'].values[0]
        # print delta_format(DT)
        # print DT/np.timedelta64(1, 'D')
        # print nh.values, HISTORY_DATE.values, HISTORY_STEP.values, HISTORY_ACTION.values, HISTORY_QCTEST_hex.values
        # print nh.values, HISTORY_DATE.values, HISTORY_STEP.values, HISTORY_ACTION.values, HISTORY_QCTEST_hex.values, HISTORY_QCTEST_int, HISTORY_QCTEST_IDs
        # if ((nh > 0) and (HISTORY_DATE != HISTORY_DATE_prev)):
        #     print "\n"
        # print nh.values, HISTORY_DATE, HISTORY_STEP.values, HISTORY_SOFTWARE.values, HISTORY_ACTION.values, HISTORY_QCTEST_hex, HISTORY_QCTEST_IDs
        # print ref.table7(HISTORY_ACTION)
        # sys.stdout.write(msg % (nh.values, str_date(HISTORY_DATE), delta_format(DT), HISTORY_STEP.values, str(HISTORY_ACTION.values).strip()))
        # sys.stdout.write(msg % (nh.values, str_date(HISTORY_DATE), delta_format(DT), ref.table12(HISTORY_STEP), ref.table7(HISTORY_ACTION)))
        # print nh.values, HISTORY_DATE, delta_format(
        #     DT), HISTORY_STEP.values, HISTORY_SOFTWARE.values, HISTORY_ACTION.values, HISTORY_QCTEST_hex, HISTORY_QCTEST_IDs
            # DT), HISTORY_STEP.values, HISTORY_SOFTWARE.values, ref.table7(HISTORY_ACTION.values), HISTORY_QCTEST_hex, HISTORY_QCTEST_IDs
        # print nh.values, DT/np.timedelta64(1, 'D'), HISTORY_STEP.values, HISTORY_SOFTWARE.values, HISTORY_ACTION.values, HISTORY_QCTEST_hex, HISTORY_QCTEST_IDs
        # print "\t", HISTORY_PARAMETER.values, HISTORY_START_PRES.values, "-", HISTORY_STOP_PRES.values, " Previous QC: ", HISTORY_PREVIOUS_VALUE.values, " / ", HISTORY_REFERENCE.values

        sys.stdout.write(msg % (nh.values, str_date(HISTORY_DATE), delta_format(DT)))
        sys.stdout.write("%35s %10s: %8s > %s\n" % (" ", "STEP", HISTORY_STEP.values, ref.table12(HISTORY_STEP)))
        sys.stdout.write("%35s %10s: %8s > %s\n" % (" ", "ACTION", HISTORY_ACTION.values, ref.table7(HISTORY_ACTION)))
        if HISTORY_QCTEST_IDs and HISTORY_QCTEST_IDs[0] != 0:
            sys.stdout.write("%35s %10s: %8s > %s\n" % (" ", "QCTEST", HISTORY_QCTEST_hex, ', '.join('{:0.0f}'.format(i) for i in HISTORY_QCTEST_IDs) ))
        else:
            sys.stdout.write("%35s %10s: %8s\n" % (" ", "QCTEST", HISTORY_QCTEST_hex ))
        if not cleanpstr(HISTORY_REFERENCE):
            sys.stdout.write("%35s %10s: %4s[%s]\n" % (" ", "SOFTWARE", cleanpstr(HISTORY_SOFTWARE), cleanpstr(HISTORY_SOFTWARE_RELEASE)))
        else:
            sys.stdout.write("%35s %10s: %4s[%s] > %s\n" % (" ", "SOFTWARE", cleanpstr(HISTORY_SOFTWARE), cleanpstr(HISTORY_SOFTWARE_RELEASE), cleanpstr(HISTORY_REFERENCE)))
        sys.stdout.write("%35s %10s: %8s\n" % (" ", "PARAMETER", cleanpstr(HISTORY_PARAMETER)))

    def print_one_entry(ds, i_prof, nh, verb=0):
        """Print data for one history entry"""
        # msg = "%1s | %20s | %16s:\n"
        # if nh==0:
        #     sys.stdout.write(msg % ('#', 'DATE', 'DATE vs CREATION'))

        HISTORY_DATE = np.datetime64(pd.to_datetime(ds['HISTORY_DATE'].sel(N_HISTORY=nh))[i_prof])  # YYYYMMDDHHMISS
        if nh > 0:
            HISTORY_DATE_prev = np.datetime64(pd.to_datetime(ds['HISTORY_DATE'].sel(N_HISTORY=nh - 1))[i_prof])
        DT = HISTORY_DATE - np.datetime64(pd.to_datetime(str(ds['DATE_CREATION'].values)))
        DTm = HISTORY_DATE - ds['JULD'].isel(N_PROF=i_prof).values

        HISTORY_STEP = ds['HISTORY_STEP'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  # From Table 12
        HISTORY_ACTION = ds['HISTORY_ACTION'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  # From Table 7

        HISTORY_QCTEST_hex = ds['HISTORY_QCTEST'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  # From Table 11
        HISTORY_QCTEST_hex = HISTORY_QCTEST_hex.astype(str).values.tostring().strip()
        if not HISTORY_QCTEST_hex:
            HISTORY_QCTEST_int = '-'
            HISTORY_QCTEST_IDs = [0]
        else:
            try:
                HISTORY_QCTEST_int = int(HISTORY_QCTEST_hex, 16)
                HISTORY_QCTEST_IDs = decodeqctest(HISTORY_QCTEST_int)
            except:
                # print("'%s'"%HISTORY_QCTEST_hex)
                # warnings.warn("Unexpected error when decoding QCTEST !", SyntaxWarning)
                # print("Unexpected error when decoding QCTEST:", sys.exc_info()[0])
                # raise
                HISTORY_QCTEST_int = 'ERROR'
                HISTORY_QCTEST_IDs = [9999]

        HISTORY_PARAMETER = ds['HISTORY_PARAMETER'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  # From Table 3
        HISTORY_START_PRES = ds['HISTORY_START_PRES'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  #
        HISTORY_STOP_PRES = ds['HISTORY_STOP_PRES'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  #
        HISTORY_PREVIOUS_VALUE = ds['HISTORY_PREVIOUS_VALUE'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  # Parameter/Flag previous value before action

        HISTORY_SOFTWARE = ds['HISTORY_SOFTWARE'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  #
        HISTORY_SOFTWARE_RELEASE = ds['HISTORY_SOFTWARE_RELEASE'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  #
        HISTORY_REFERENCE = ds['HISTORY_REFERENCE'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  #
        HISTORY_INSTITUTION = ds['HISTORY_INSTITUTION'].sel(N_HISTORY=nh).isel(N_PROF=i_prof)  # From Table 4

        if verb==1:
            blk = "".join([" "] * 4)
            empty_STEP = not cleanpstr(HISTORY_STEP)
            sys.stdout.write(
                "%1s | %4s: '%8s' > %s\n" % (nh.values, "STEP", cleanpstr(HISTORY_STEP), ref.table12(HISTORY_STEP)))
            # sys.stdout.write("%s %12s: '%19s' > %s since creation\n" % (blk, "DATE", str_date(HISTORY_DATE), delta_format(DT)))
            sys.stdout.write("%s %12s: '%19s' > %s since creation, %s since measurement\n" % (
            blk, "DATE", str_date(HISTORY_DATE), delta_format(DT), delta_format(DTm)))
            sys.stdout.write("%s %12s: '%s' > %s\n" % (
            blk, "INSTITUTION", cleanpstr(HISTORY_INSTITUTION), ref.table4(HISTORY_INSTITUTION)))

            if not cleanpstr(HISTORY_REFERENCE):
                sys.stdout.write(
                    "%s %12s: '%s', release '%s'\n" % (
                    blk, "SOFTWARE", cleanpstr(HISTORY_SOFTWARE), cleanpstr(HISTORY_SOFTWARE_RELEASE)))
            else:
                sys.stdout.write(
                    "%s %12s: '%s', release '%s', reference '%s'\n" % (blk, "SOFTWARE", cleanpstr(HISTORY_SOFTWARE),
                                                                       cleanpstr(HISTORY_SOFTWARE_RELEASE),
                                                                       cleanpstr(HISTORY_REFERENCE)))

            empty_ACTION = not HISTORY_ACTION.values
            empty_QCTEST = not (HISTORY_QCTEST_IDs and HISTORY_QCTEST_IDs[0] != 0)
            empty_QCchge = not str(HISTORY_PREVIOUS_VALUE.values)
            empty_PARAM = not cleanpstr(HISTORY_PARAMETER)
            empty_START = not str(HISTORY_START_PRES)

            if not empty_ACTION:
                sys.stdout.write(
                    "%s %12s: '%4s' > %s\n" % (blk, "ACTION", HISTORY_ACTION.values, ref.table7(HISTORY_ACTION)))

            if not empty_QCTEST:
                if HISTORY_QCTEST_IDs[0] != 9999:
                    sys.stdout.write(
                        "%s %12s: '%s' > %s\n" % (
                        blk, "QCTEST", HISTORY_QCTEST_hex, ', '.join('{:0.0f}'.format(i) for i in HISTORY_QCTEST_IDs)))
                else:
                    sys.stdout.write(
                        # "%s %12s: %s\n" % (blk, "QCTEST", "<< Unexpected error when decoding QCTEST ! >>"))
                        "%s %12s: %s\n" % (blk, "QCTEST",
                                           ("<< Unexpected error when decoding QCTEST='%s' ! >>")%(str(HISTORY_QCTEST_hex))))

            if not empty_PARAM:
                sys.stdout.write("%s %12s: '%s'\n" % (blk, "PARAMETER", cleanpstr(HISTORY_PARAMETER)))

            if not empty_START:
                sys.stdout.write(
                    "%s %12s: From '%0.1f' to '%0.1f'\n" % (blk, "PRES", HISTORY_START_PRES, HISTORY_STOP_PRES))
            if not empty_QCchge:
                sys.stdout.write(
                    "%s %12s\n%s %12s: '%4s'\n" % (blk, "PREVIOUS", blk, "VALUE", str(HISTORY_PREVIOUS_VALUE.values)))

            missing_list = []
            if empty_STEP:
                missing_list.append("STEP")
            if empty_ACTION:
                missing_list.append("ACTION")
            if empty_QCTEST:
                missing_list.append("QCTEST")
            if empty_PARAM:
                missing_list.append("PARAM")
            if empty_START:
                missing_list.append("START_PRES")
            if empty_QCchge:
                missing_list.append("PREVIOUS_VALUE")
            if len(missing_list):
                sys.stdout.write("%s %12s: %s\n" % (blk, "Missing", ", ".join(missing_list)))

        elif verb==0:
            blk = "".join([" "] * 4)
            # sys.stdout.write(
            #     "%1s | %4s: '%8s' > %s, %s since creation, %s since measurement\n" % (nh.values, "STEP",
            #     cleanpstr(HISTORY_STEP), str_date(HISTORY_DATE), delta_format(DT), delta_format(DTm)))
            # sys.stdout.write(
            #     "%s > %s\n" % (blk, ref.table12(HISTORY_STEP)))
            sys.stdout.write(
                "%1s | %19s | %s \n" % (nh.values, str_date(HISTORY_DATE), ref.table12(HISTORY_STEP) ))
    #
    M = ds['JULD'].isel(N_PROF=i_prof).values
    C = np.datetime64(pd.to_datetime(str(ds['DATE_CREATION'].values)))
    DT = C - M
    U = np.datetime64(pd.to_datetime(str(ds['DATE_UPDATE'].values)))
    DTu = U - C
    print "    PROFILE NUMBER: %i" % (i_prof)
    print "  MEASUREMENT DATE: %s ('JULD')" % (str_date(M))
    print "FILE CREATION DATE: %s, %s since measurement ('DATE_CREATION')" % (str_date(C), delta_format(DT))
    print "  FILE UPDATE DATE: %s, %s since creation ('DATE_UPDATE')" % (str_date(U), delta_format(DTu))

    print "         HISTORY:"
    for nh in ds['N_HISTORY']:
        print_one_entry(ds, i_prof, nh, verb=verb)

# ncdhistory aoml/1900143/profiles/D1900143_300.nc
# ncdhistory aoml/1900143/profiles/D1900143_065.nc
# ncdhistory coriolis/6900697/profiles/R6900697_005.nc
# ncdhistory csio/2901552/profiles/R2901552_372.nc
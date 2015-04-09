#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# extract atmopsheric forcing and state variables from NOMADS obtained NARR for LDAS
# input data are located in INROOT
# output in grib format and are located in OUTROOT
# usage: PROG INROOT OUTROOT

import os.path
import io
import subprocess
import dateutil.parser
import dateutil.rrule

# value format:
# [narr_file_suffix, level_list]
IFLNM_FMT = 'narr-{subset}_221_{year:04d}{month:02d}{day:02d}_{hour:02d}00_000.grb'
IDIR_FMT = '{year:04d}{month:02d}/{year:04d}{month:02d}{day:02d}'
HOURDELTA = 3

def extract(ipatha, ipathb, outroot, dt, outflatdir=False):
    ODIR_FMT = '{var:s}'
    OFLNM_FMT = 'NARR_{var}_{inv}.{year:04d}{month:02d}{day:02d}{hour:02d}.grb'
    WGRIB_EXE = 'wgrib'
    VARIABLES = {'TSOIL' : ['0-10', '10-40', '40-100', '100-200'],
                 'SOILW' : ['0-10', '10-40', '40-100', '100-200'],
                 'TMP'   : ['sfc', '30 m'],
                 'CNWAT' : ['sfc',],
                 'WEASD' : ['sfc',],
                 'PRES'  : ['30 m',],
                 'SPFH'  : ['30 m',],
                 'UGRD'  : ['30 m',],
                 'VGRD'  : ['30 m',],
                 'APCP'  : ['sfc'],
                 'DLWRF' : ['sfc:0-3hr'],
                 'DSWRF' : ['sfc:0-3hr']}
    # dump inputs
    dumpa = subprocess.check_output([WGRIB_EXE, ipatha, '-s'], universal_newlines=True)
    dumpb = subprocess.check_output([WGRIB_EXE, ipathb, '-s'], universal_newlines=True)
    for var, invs in VARIABLES.items():
        for inv in invs:
            if outflatdir:
                opath = os.path.join(outroot,
                                     OFLNM_FMT.format(year=dt.year, month=dt.month, day=dt.day,
                                                      hour=dt.hour,
                                                      var=var,
                                                      inv=inv.replace(':','').replace(' ','')))
            else:
                opath = os.path.join(outroot, ODIR_FMT.format(var=var),
                                     OFLNM_FMT.format(year=dt.year, month=dt.month, day=dt.day,
                                                      hour=dt.hour,
                                                      var=var,
                                                      inv=inv.replace(':','').replace(' ','')))
            # make output directory
            os.makedirs(os.path.dirname(opath), exist_ok=True)
            # ipatha
            inva = ''.join(x for x in io.StringIO(dumpa)
                           if ':{var:s}:{inv:s}'.format(var=var,inv=inv) in x)
            ext = subprocess.Popen([WGRIB_EXE, ipatha, '-i', '-grib', '-o', opath],
                                   stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                   universal_newlines=True)
            ext.communicate(input=inva)
            # ipathb
            invb = ''.join(x for x in io.StringIO(dumpb)
                           if ':{var:s}:{inv:s}'.format(var=var,inv=inv) in x)
            ext = subprocess.Popen([WGRIB_EXE, ipathb, '-i', '-grib', '-append', '-o', opath],
                                   stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                   universal_newlines=True)
            ext.communicate(input=invb)
    return

def main(inroot=None, outroot=None, dtbeg=None, dtend=None,
         inflatdir=False, outflatdir=False, verbosity=True):
    if (inroot is None) or (outroot is None) or (dtbeg is None) or (dtend is None):
        return
    for dt in dateutil.rrule.rrule(dateutil.rrule.HOURLY, interval=HOURDELTA,
                                   dtstart=dtbeg,
                                   until=dtend):
        if dt >= dtend: continue # exclude the dtend
        if verbosity: print(dt.strftime('%Y-%m-%dT%H:%M:%S ... '), end='', flush=True)
        if inflatdir:
            ipatha = os.path.join(inroot,
                                  IFLNM_FMT.format(year=dt.year, month=dt.month, day=dt.day,
                                                   hour=dt.hour,
                                                   subset='a'))
            ipathb = os.path.join(inroot,
                                  IFLNM_FMT.format(year=dt.year, month=dt.month, day=dt.day,
                                                   hour=dt.hour,
                                                   subset='b'))
        else:
            ipatha = os.path.join(inroot,
                                  IDIR_FMT.format(year=dt.year, month=dt.month, day=dt.day),
                                  IFLNM_FMT.format(year=dt.year, month=dt.month, day=dt.day,
                                                   hour=dt.hour,
                                                   subset='a'))
            ipathb = os.path.join(inroot,
                                  IDIR_FMT.format(year=dt.year, month=dt.month, day=dt.day),
                                  IFLNM_FMT.format(year=dt.year, month=dt.month, day=dt.day,
                                                   hour=dt.hour,
                                                   subset='b'))
        if (not os.path.isfile(ipatha)) and (not os.path.isfile(ipathb)):
            if verbosity : print('Error[file ' + ipatha + ';' + ipathb +'].')
            continue
        elif not os.path.isfile(ipatha):
            if verbosity: print('Error[file ' + ipatha + '].')
            continue
        elif not os.path.isfile(ipathb):
            if verbosity: print('Error[file ' + ipathb + '].')
            continue
        extract(ipatha, ipathb, outroot, dt, outflatdir=outflatdir)
        if verbosity: print('Done.')
    return

import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract NOMADS obtained NARR for LDAS.')
    parser.add_argument('inroot',
                        help='root directory of input data', type=str)
    parser.add_argument('outroot',
                        help='root directory for output', type=str)
    parser.add_argument('-b', '--begtime',
                        help='start date and time (default: 19790101T00)',
                        default='19790101T00', type=str)
    parser.add_argument('-e', '--endtime',
                        help='end date and time (exclusive, default: 20140101T00)',
                        default='20140101T00', type=str)
    parser.add_argument('-if', '--inflatdir',
                        help='all input file in one directory',
                        default=False, action='store_true')
    parser.add_argument('-of', '--outflatdir',
                        help='all output file in one directory',
                        default=False, action='store_true')
    parser.add_argument('-v', '--verbosity',
                        help='explain what is being done', action='store_true')
    args = parser.parse_args()

    main(inroot=os.path.abspath(args.inroot),
         outroot=os.path.abspath(args.outroot),
         dtbeg=dateutil.parser.parse(args.begtime),
         dtend=dateutil.parser.parse(args.endtime),
         inflatdir=args.inflatdir,
         outflatdir=args.outflatdir,
         verbosity=args.verbosity)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division, print_function

# download NARR (for NoahMP and WRF) from nomads

import sys
import os
import os.path
import urllib.request
import urllib.error
import subprocess
import time
from datetime import datetime, timedelta

RROOT = 'ftp://nomads.ncdc.noaa.gov/NARR'
FOLD_TMP = '{year:04d}{month:02d}/{year:04d}{month:02d}{day:02d}'
FLNM_TMP = 'narr-{subset:1s}_221_{year:04d}{month:02d}{day:02d}_{hour:02d}00_000.grb'
DATETIME_DELTA = timedelta(hours=3)

def download_file(rpath, lpath):
    """
    download file from rpath to lpath
    try globus-url-copy firstly, then urllib
    """
    os.makedirs(os.path.dirname(lpath), exist_ok=True)
    
    # globus-url-copy
    try :
        DLD_EXE='globus-url-copy'
        DLD_OPT='-q'
        subprocess.check_call([DLD_EXE, DLD_OPT, rpath, lpath],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    except:
        pass
        
    # urllib
    MAXTRY = 3
    for itry in range(MAXTRY):
        try:
            req = urllib.request.Request(rpath)
            with open(lpath, 'wb') as lf, \
                 urllib.request.urlopen(req) as rf:
                lf.write(rf.read())
            break
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            if itry < MAXTRY - 1:
                time.sleep(0.5)
            else:
                raise e
        except Exception as e:
            raise e
    return

def download_dataset(root='.', begtime=None, endtime=None, subset=None,
         flatdir=False, verbosity=False):
    if subset is None:
        subset = ['a',]
    dt = begtime
    while dt < endtime:
        for ss in subset:
            fold = FOLD_TMP.format(year=dt.year, month=dt.month, day=dt.day)
            flnm = FLNM_TMP.format(subset=ss,
                                    year=dt.year, month=dt.month, day=dt.day, hour=dt.hour)
            if flatdir:
                lpath = os.path.join(root, flnm)
            else:
                lpath = os.path.join(root, fold, flnm)
            rpath = os.path.join(RROOT, fold, flnm)
            if verbosity: print(os.path.basename(rpath) + ' ... ', end='',flush=True)
            try:
                download_file(rpath, lpath)
                if verbosity: print('Done.')
            except:
                if verbosity: print('Error.')
        dt += DATETIME_DELTA
    pass

import argparse
import dateutil.parser
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download NARR 3-hourly product from NOMADS.')
    parser.add_argument('-s', '--subset',
                        help='subset (a or b, default: a,b)',
                        default='a,b', type=str)
    parser.add_argument('-r', '--root',
                        help='root directory for local storage (default: current directory)',
                        default=os.getcwd(), type=str)
    parser.add_argument('-b', '--begtime',
                        help='start date and time (default: 19790101T00)',
                        default='19790101T00', type=str)
    parser.add_argument('-e', '--endtime',
                        help='end date and time (exclusive, default: 20140101T00)',
                        default='20140101T00', type=str)
    parser.add_argument('-f', '--flatdir',
                        help='download all file into one directory',
                        default=False, action='store_true')
    parser.add_argument('-v', '--verbosity',
                        help='explain what is being done', action='store_true')
    args = parser.parse_args()
    if args.subset:
        subset = [x.lower() for x in args.subset.split(',') if x.lower() in ('a', 'b')]
        if subset == set():
            print('ERROR: ', subset, ' is(are) not valid subset')
            print('valid subset: a or b')
            sys.exit(1)
    download_dataset(root=args.root,
                     begtime=dateutil.parser.parse(args.begtime),
                     endtime=dateutil.parser.parse(args.endtime),
                     subset=subset,
                     flatdir=args.flatdir,
                     verbosity=args.verbosity)

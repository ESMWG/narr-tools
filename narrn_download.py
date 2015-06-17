#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division, print_function

# description: Download NARR from nomads.
# author: Hui ZHENG
# email: woolf1988@qq.com

import sys
import os.path
import urllib.request
import urllib.error
import subprocess
import time
import datetime

RROOT = 'ftp://nomads.ncdc.noaa.gov/NARR'
DIR_TMP = '{year:04d}{month:02d}/{year:04d}{month:02d}{day:02d}'
FLNM_TMP = 'narr-{subset:1s}_221_{year:04d}{month:02d}{day:02d}_{hour:02d}00_000.grb'
TIME_DELTA = datetime.timedelta(hours=3)

def download_file(rpath, lpath):
    """
    download file from rpath to lpath
    try globus-url-copy firstly, then urllib
    """
    os.makedirs(os.path.dirname(lpath), exist_ok=True)
    
    # globus-url-copy
    try:
        DLD_EXE='globus-url-copy'
        DLD_OPT='-q'
        subprocess.check_call([DLD_EXE, DLD_OPT, rpath, lpath],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    except Exception:
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
    if subset is None or subset == '':
        subset = 'a'
    dt = begtime
    while dt < endtime:
        for ss in subset:
            fold = DIR_TMP.format(year=dt.year, month=dt.month, day=dt.day)
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
            except KeyboardInterrupt as e:
                return
            except Exception:
                if verbosity: print('Error.')
        dt += TIME_DELTA
    return

import argparse
import dateutil.parser
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download NARR 3-hourly product from NOMADS.')
    parser.add_argument('root', type=str,
                        help='root directory for local storage')
    parser.add_argument('-s', '--subset', choices=['a', 'b', 'ab'],
                        help='subset (default: ab)',
                        default='ab', type=str)
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
    try:
        os.makedirs(args.root, exist_ok=True)
    except:
        print('unable to write directory: ' + args.root, file=sys.stderr)
        sys.exit(1)
    download_dataset(root=os.path.abspath(args.root),
                     begtime=dateutil.parser.parse(args.begtime),
                     endtime=dateutil.parser.parse(args.endtime),
                     subset=args.subset,
                     flatdir=args.flatdir,
                     verbosity=args.verbosity)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author: Hui ZHENG

import os.path
import datetime
import subprocess
import tempfile
import argparse
import dateutil.parser
import dateutil.rrule

FILL_DSWRF_NARR_EXE = 'narr_filldswrf4ldas.exe'
NARRLAT = 'NARRLAT.txt'
NARRLON = 'NARRLON.txt'
HOURDELTA = 3

def fill_dswrf_narr(ipath, idt, root, flatdir=False):
    ODIR = 'DSWRF24'
    OFLNM_FMT = 'NARR_DSWRF_sfc0-1hr.{year:04d}{month:02d}{day:02d}{hour:02d}.grb'
    with tempfile.NamedTemporaryFile(mode='wt',dir=os.getcwd(), delete=True) as fin:
        fin.write(ipath+'\n')
        for ihr in range(HOURDELTA):
            dt = idt + datetime.timedelta(hours=ihr)
            oflnm = OFLNM_FMT.format(year=dt.year, month=dt.month, day=dt.day, hour=dt.hour)
            if flatdir:
                opath = os.path.join(root, oflnm)
            else:
                opath = os.path.join(root, ODIR, oflnm)
            fin.write(opath+'\n')
            fin.write(dt.strftime('%y %m %d %H %j %H\n'))
            fin.flush()
        os.makedirs(os.path.dirname(opath), exist_ok=True)
        try:
            subprocess.check_call([FILL_DSWRF_NARR_EXE, NARRLAT, NARRLON, fin.name],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            raise e
    return

def main(root=None, dtbeg=None, dtend=None,
         flatdir=False, verbosity=True):
    IDIR = 'DSWRF'
    IFLNM_FMT = 'NARR_DSWRF_sfc0-3hr.{year:04d}{month:02d}{day:02d}{hour:02d}.grb'
    if (root is None) or (dtbeg is None) or (dtend is None):
        return
    for dt in dateutil.rrule.rrule(dateutil.rrule.HOURLY,
                                   interval=HOURDELTA,
                                   dtstart=dtbeg,
                                   until=dtend):
        if dt >= dtend:
            continue # exclude dtend
        if verbosity:
            print(dt.strftime('%Y-%m-%dT%H:%M:%S ... '), end='', flush=True)
        iflnm = IFLNM_FMT.format(year=dt.year, month=dt.month, day=dt.day, hour=dt.hour)
        if flatdir:
            ipath = os.path.join(root, iflnm)
        else:
            ipath = os.path.join(root, IDIR, iflnm)
        if (not os.path.isfile(ipath)):
            if verbosity: print('Error: file (' + ipath + ') does not exist!')
            continue
        
        try:
            fill_dswrf_narr(ipath, dt, root, flatdir=flatdir)
            if verbosity: print('Done.')
        except:
            if verbosity: print('Error.')
    return

if __name__ == '__main__':
    if os.path.dirname(FILL_DSWRF_NARR_EXE) == '':
        FILL_DSWRF_NARR_EXE = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            FILL_DSWRF_NARR_EXE)
    if os.path.dirname(NARRLAT) == '':
        NARRLAT = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            NARRLAT)
    if os.path.dirname(NARRLON) == '':
        NARRLON = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            NARRLON)
    for f in [FILL_DSWRF_NARR_EXE, NARRLAT, NARRLON]:
        if not os.path.isfile(f):
            print('Unable to find file: ' + f)
            exit(1)
    parser = argparse.ArgumentParser(description='Fill hourly DSWRF from 3-hourly data.')
    parser.add_argument('root',
                        help='data root directory', type=str)
    parser.add_argument('-b', '--begtime',
                        help='start date and time (default: 19790101T00)',
                        default='19790101T00', type=str)
    parser.add_argument('-e', '--endtime',
                        help='end date and time (exclusive, default: 20140101T00)',
                        default='20140101T00', type=str)
    parser.add_argument('-f', '--flatdir',
                        help='all file in one directory',
                        default=False, action='store_true')
    parser.add_argument('-v', '--verbosity',
                        help='explain what is being done', action='store_true')
    args = parser.parse_args()

    main(root=os.path.abspath(args.root),
         dtbeg=dateutil.parser.parse(args.begtime),
         dtend=dateutil.parser.parse(args.endtime),
         flatdir=args.flatdir,
         verbosity=args.verbosity)

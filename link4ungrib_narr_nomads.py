#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# create symbolic link (GRIBFILE.XXX) to NARR for using in ungrib
# author: Hui ZHENG
# email: woolf1988@qq.com
# date: 2015-03-21

import sys
import os
import os.path
import glob
import string
import itertools
import datetime

LINK_PREFIX='GRIBFILE.'
DIR_TMP = '{year:04d}{month:02d}/{year:04d}{month:02d}{day:02d}'
FLNM_TMP = 'narr-{subset:1s}_221_{year:04d}{month:02d}{day:02d}_{hour:02d}00_000.grb'
TIME_DELTA = datetime.timedelta(hours=3)

def globfiles(srcroot=None, dtbeg=None, dtend=None, subset=None, flatdir=False):
    """glob narr files"""
    if (srcroot is None) or (dtbeg is None) or (dtend is None):
        return
    if not os.path.isdir(srcroot):
        print('Error: directory (' + srcroot + ') does not exist!')
        return
    if subset is None:
        subset = 'a'
    
    files = []

    dt = dtbeg
    while dt < dtend:
        for ss in subset:
            fold = DIR_TMP.format(year=dt.year, month=dt.month, day=dt.day)
            flnm = FLNM_TMP.format(subset=ss,
                                   year=dt.year, month=dt.month, day=dt.day, hour=dt.hour)
            if flatdir:
                path = os.path.join(srcroot, flnm)
            else:
                path = os.path.join(srcroot, fold, flnm)
            if os.path.isfile(path):
                files.append(path)
        dt += TIME_DELTA
    return files
    
def linkfiles(files, desroot):
    """create link to filelist in desroot"""
    if not os.path.isdir(desroot):
        print('Error: directory (' + desroot + ') does not exist!')
        return
    if not os.access(desroot, os.W_OK):
        print('Error: directory (' + desroot + ') does not writable!')
        return
    
    for oldfile in glob.glob(os.path.join(desroot,LINK_PREFIX+'*')):
        os.remove(oldfile)

    suffixes = (''.join([s1, s2, s3]) for (s1, s2, s3) in
                itertools.product(string.ascii_uppercase,
                                  string.ascii_uppercase,
                                  string.ascii_uppercase))
    linknum = 0
    for srcfile, link_suffix in zip(files, suffixes):
        os.symlink(srcfile, os.path.join(desroot, LINK_PREFIX + link_suffix))
        linknum += 1
    if len(files) > linknum:
        print('Warning: ran out of grib file suffixes!')
    
    return

import argparse
import dateutil.parser
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create symbolic links to NARR.',
        epilog='The link names are in format ' + LINK_PREFIX + 'XXX' +
        ' and can be used for WPS/ungrib.')
    parser.add_argument('srcroot', type=str,
                        help='root directory of NARR')
    parser.add_argument('desroot', type=str, nargs='?', default=os.getcwd(),
                        help='root directory of symbolic links (default: current directory)')
    parser.add_argument('-s', '--subset', choices=['a', 'b', 'ab', 'ba'],
                        help='subset (default: a)',
                        default='a', type=str)
    parser.add_argument('-b', '--begtime',
                        help='start date and time (default: 19790101T00)',
                        default='19790101T00', type=str)
    parser.add_argument('-e', '--endtime',
                        help='end date and time (exclusive, default: 20140101T00)',
                        default='20140101T00', type=str)
    parser.add_argument('-f', '--flatdir',
                        help='NARR data file in one directory',
                        default=False, action='store_true')
    args = parser.parse_args()
    
    files = globfiles(srcroot=args.srcroot,
                      dtbeg=dateutil.parser.parse(args.begtime),
                      dtend=dateutil.parser.parse(args.endtime),
                      subset=args.subset,
                      flatdir=args.flatdir)
    linkfiles(files, args.desroot)

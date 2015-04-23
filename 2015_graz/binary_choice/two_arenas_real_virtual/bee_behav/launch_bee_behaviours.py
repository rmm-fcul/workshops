#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import signal
import subprocess
#import sys
import time, datetime
import argparse
import csv

from assisipy_simtools.arena import enki_prep

'''
# The os.setsid() is passed in the argument preexec_fn so
# it's run after the fork() and before  exec() to run the shell.
pro = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            shell=True, preexec_fn=os.setsid)

os.killpg(pro.pid, signal.SIGTERM)  # Send the signal to all the process groups
'''

def read_bee_names(fname, verb=False):
    '''
    uses specification parser that is maintained with writer!
    (which provides structured data)

    returns a list of bees and their publish addresses
    '''

    bees = []
    pub_sub = []
    specs = []
    with open(fname, 'r') as fh:
        R = csv.reader(fh, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL,
                skipinitialspace=True)
        for row in R:
            specs.append(row)
            print len(row)


    for (ty, name, x, y, yaw, pub_addr, sub_addr,)  in specs:
        if ty.lower() == 'bee':
            bees.append(name)
            pub_sub.append( (pub_addr, sub_addr) )
    return bees, pub_sub




def _old_read_bee_names(fname):
    '''
    assumes that the object file is of the form
       objtype, objname, x, y, theta, pub_addr, sub_addr
       objtype, objname, x, y, theta, pub_addr, sub_addr
       objtype, objname, x, y, theta, pub_addr, sub_addr
       objtype, objname, x, y, theta, pub_addr, sub_addr
    where objtype can be [bee, casu, physical, ...]

    returns a list of all the names of bees.
    [envisaged is to allow heterogeneous programs to be run, but right now
    one behaviour for all bees -- could either generate multiple lists, or
    filter the lists then run this program multiple times to allow for
    hereogeneity]
    '''

    with open(fname, 'r') as f:
        lines = f.read()

    bees = []
    pub_sub = []
    for line in (l for l in lines.split() if not l.startswith('#')):
        _fields = line.split(';')
        fields = [f.strip('"') for f in _fields]
        #print fields
        if len(fields):
            if fields[0].lower() == 'bee':
                bees.append(fields[1])
                if len(fields) >= 7:
                    pub_sub.append( (fields[5], fields[6]) )
    return bees, pub_sub

if __name__ == '__main__':
    ''' execute the handler for all bees in the bee list '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-ol', '--obj-listing', type=str, required=True,
            help='file listing all objects spawned in enki simulator') # no default
    parser.add_argument('--logpath', type=str, required=True,
                        help="path to record output in")
    parser.add_argument('-lc', '--local-conf', type=str, default=None,
            help='local configuration for bee behaviour')
    parser.add_argument('-e', '--exec-script', type=str, default='./bee_behav.py',
            help='name of script to execute for each bee in `bee-file`')
    args = parser.parse_args()


    bee_names, addrs = read_bee_names(args.obj_listing)
    print "[I] {} bees to run with behaviour '{}'".format(
            len(bee_names), args.exec_script)
    for name in bee_names:
        print name

    #[ name + "\n" for name in bee_names]

    # any of the live crud goes in a single file
    logfile = "bee_output.txt"
    f = open(logfile, 'w')
    f.close() # clear the logfile



    print "Started at:",  datetime.datetime.fromtimestamp(time.time())

    lc = ""
    if args.local_conf is not None:
        lc = "-c {}".format(args.local_conf)

    # launch n bee handlers
    p_handles = []
    for name, p_s in zip(bee_names, addrs):
        print "Launching bee '{}'".format(name)
        to_exec = "python {cmd} --logpath={logpath} -bn {beename} -sa {sub} -pa {pub} {lc} #>> {lf}".format(
            cmd=args.exec_script, beename=name, logpath=args.logpath, lf=logfile,
            pub=p_s[0], sub=p_s[1], lc=lc,
        )
        print "  ", to_exec

        p = subprocess.Popen(to_exec, shell=True)
        #p = subprocess.Popen(to_exec, stdout=subprocess.PIPE, shell=True)
        #p = subprocess.Popen('python {} {} >> {}'.format(
        #    args.exec_script, name, logfile),
        #        stdout=subprocess.PIPE, shell=True) #, preexec_fn=os.setsid)
        p_handles.append(p)

    pids = [_p.pid for _p in p_handles]
    print "[I] PIDs are", pids
    print " type kill -9 ", pids

    # wait for the user to ctrl-c, then kill all the individual scrupts
    try:
        print "[I] wrapper has pid", os.getpid()
        while True:
            pass
    except KeyboardInterrupt:
        print "shutting down..."
        for  p in p_handles:
            print "  killing process ", p.pid
            #os.kill(p.pid, signal.CTRL_BREAK_EVENT)
            os.kill(p.pid, signal.SIGINT)


    time.sleep(0.5)
    print "[] (bee behav wrapper) Finished at:",  datetime.datetime.fromtimestamp(time.time())

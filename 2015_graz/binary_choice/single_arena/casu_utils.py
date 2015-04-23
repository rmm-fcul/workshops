#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
a library of functions used in CASU controller dynamics. Got a lot of
messy code that would be neater like this

RM, Feb 2015

'''

import numpy as np
from assisipy import casu
#import matplotlib.cm as cm
from datetime import datetime
import parsing
import time

### ============= maths ============= ###

#{{{ rolling_avg
def rolling_avg(x, n):
    '''
    given the sample x, provide a rolling average taking n samples per data point.
    NOT a quick solution, but easy...
    '''
    y = np.zeros((len(x),))
    for ctr in range(len(x)):
        y[ctr] = np.sum(x[ctr:(ctr+n)])

    return y/n
#}}}

### ============= general behaviour ============= ###

#{{{ measure_ir_sensors
def measure_ir_sensors(mycasu, detect_data):
    ''' count up sensors that detect a bee, plus rotate history array '''

    # don't discriminate between specific directions, so just accumulate all
    count = 0
    for (val,t) in zip(mycasu.get_ir_raw_value(casu.ARRAY), mycasu.threshold):
        if (val > t):
            count += 1

    #print "raw:", 
    #print ",".join(["{:.2f}".format(x) for x in mycasu.get_ir_raw_value(casu.ARRAY)])
    #mycasu.total_count += count # historical count over all time
    detect_data = np.roll(detect_data, 1) # step all positions back
    detect_data[0] = count      # and overwrite the first entry (this was rolled
    # around, so is the oldest entry -- and to become the newest now)
    # allow ext usage to apply window -- remain agnostic here during collection.
    return detect_data, count

#}}}
#{{{ heater_one_step
def heater_one_step(h):
    '''legacy function'''
    return detect_bee_proximity_saturated(h)

def detect_bee_proximity_saturated(h):
    # measure proximity
    detect_data, count = measure_ir_sensors(h, h.detect_data)
    h.detect_data = detect_data
    # overall bee count for this casu
    sat_count = min(h.sat_lim, count) # saturates
    return sat_count
#}}}

#{{{ find_mean_ext_temp
def find_mean_ext_temp(h):
    r = []
    for sensor in [casu.TEMP_F, casu.TEMP_B, casu.TEMP_L, casu.TEMP_R ]:
        r.append(h.get_temp(sensor))

    if len(r):
        mean = sum(r) / float(len(r))
    else:
        mean = 0.0

    return mean
#}}}

### ============= inter-casu comms ============= ###
#{{{ comms functions
def transmit_my_count(h, sat_count, dest='accomplice'):
    s = "{}".format(sat_count)
    if h.verb > 1:
        print "\t[i]==> {} send msg ({} by): '{}' bees, to {}".format(
            h._thename, len(s), s, dest)
    h.send_message(dest, s)


#TODO: this is non-specific, i.e., any message from anyone is assumed to have
# the right form.  For heterogeneous neighbours, we need to check identity as
# well

def recv_all_msgs(h, retry_cnt=0, max_recv=None):
    '''
    continue to read message bffer until no more messages.
    as list of parsed messages parsed into (src, float) pairs
    '''
    msgs = []
    try_cnt = 0

    while(True):
        msg = h.read_message()
        #print msg
        if msg:
            txt = msg['data'].strip()
            src = msg['sender']
            bee_cnt = float(txt.split()[0])
            msgs.append((src, bee_cnt))

            if h.verb >1:
                print "\t[i]<== {3} recv msg ({2} by): '{1}' bees, {4} from {0} {5}".format(
                    msg['sender'], bee_cnt, len(msg['data']), h._thename,
                    BLU, ENDC)

            if h.verb > 1:
                #print dir(msg)
                print msg.items()

            if(max_recv is not None and len(msgs) >= max_recv):
                break
        else:
            # buffer emptied, return
            try_cnt += 1
            if try_cnt > retry_cnt:
                break

    return msgs


def recv_neighbour_msg(h):
    bee_cnt = 0
    msg = h.read_message()
    #print msg
    if msg:
        txt = msg['data'].strip()
        bee_cnt = int(txt.split()[0])
        if h.verb >1:
            print "\t[i]<== {3} recv msg ({2} by): '{1}' bees, from {0}".format(
                msg['sender'], bee_cnt, len(msg['data']), h._thename)

    return bee_cnt;

def recv_neighbour_msg_w_src(h):
    ''' provide the source of a message as well as the message count'''
    bee_cnt = 0
    src = None
    msg = h.read_message()
    #print msg
    if msg:
        txt = msg['data'].strip()
        src = msg['sender']
        bee_cnt = float(txt.split()[0])
        if h.verb >1:
            print "\t[i]<== {3} recv msg ({2} by): '{1}' bees, from {0}".format(
                msg['sender'], bee_cnt, len(msg['data']), h._thename)
        if h.verb > 1:
            #print dir(msg)
            print msg.items()

    return bee_cnt, src


def recv_neighbour_msg_flt(h):
    bee_cnt = 0
    msg = h.read_message()
    #print msg
    if msg:
        txt = msg['data'].strip()
        bee_cnt = float(txt.split()[0])
        if h.verb > 1:
            print "\t[i]<== {3} recv msg ({2} by): '{1}' bees, from {0}".format(
                msg['sender'], bee_cnt, len(msg['data']), h._thename)

    return bee_cnt;

#}}}

def find_comms_mapping(name, rtc_path, suffix='-sim', verb=True):
    links = parsing.find_comm_link_mapping(
            name, rtc_path=rtc_path, suffix=suffix, verb=verb)
    if verb:
        print "[I] for {}, found the following nodes/edges".format(name)
        print "\t", links.items()
        print "\n===================================\n\n"
    return links



### ============= display ============= ###

#{{{ term codes for colored text
ERR = '\033[41m'
BLU = '\033[34m'
ENDC = '\033[0m'
#}}}
#{{{ color funcs
#def gen_cmap(m='hot', n=32) :
#    return cm.get_cmap(m, n) # get LUT with 32 values -- some gradation but see steps

def gen_clr_tgt(new_temp, cmap, tgt=None, min_temp=28.0, max_temp=38.0):
    t_rng = float(max_temp - min_temp)
    fr = (new_temp - min_temp) / t_rng
    i = int(fr * len(cmap))
    # compute basic color, if on target
    #r,g,b,a = cmap(i)
    g = 0.0; b = 0.0; a = 1.0;
    
    i = sorted([0, i, len(cmap)-1])[1]
    r = cmap[i]

    # now adjust according to distance from target
    if tgt is None: tgt=new_temp

    dt = np.abs(new_temp - tgt)
    dt_r = dt / t_rng
    h2 = np.array([r,g,b])
    h2 *= (1-dt_r)

    return h2

# a colormap with 8 settings, taht doesn't depend on the presence of
# matplotlib (hard-coded though.) -- depricating
_clrs = [
        (0.2, 0.2, 0.2),
        (0.041, 0, 0),
        (0.412, 0, 0),
        (0.793, 0, 0),
        (1, 0.174, 0),
        (1, 0.555, 0),
        (1, 0.936, 0),
        (1, 1, 0.475),
        (1, 1, 1),
        ]

_dflt_clr = (0.2, 0.2, 0.2)

# can access other gradations of colour using M = cm.hot(n) for n steps, then
# either extract them once (`clrs = M(arange(n)`) or each time ( `clr_x = M(x)`)
# BT here we're going to use 8 steps for all CASUs so no bother.

#}}}

def sep_with_nowtime():
    print "# =================== t={} =================== #\n".format(
        datetime.now().strftime("%H:%M:%S"))

### ============= more generic ============= ###
#{{{ a struct constructor
# some handy python utilities, from Kier Dugan
class Struct:
  def __init__ (self, **kwargs):
    self.__dict__.update (kwargs)

  def get(self, key, default=None):
      return self.__dict__.get(key, default)


  def addFields(self, **kwargs):
    # add other fields (basically variables) after initialisation
    self.__dict__.update (kwargs)

#}}}



### calibraiont
def _calibrate(h, calib_steps, calib_gain=1.1, interval=0.1):
    '''
    read the sensors several times, and take the highest reading
    seen as the threshold.
    '''
    h._raw_thresh = [0] * 7 # default cases for threshold
    for stp in xrange(calib_steps):
        for i, v in enumerate(h.get_ir_raw_value(casu.ARRAY)):
            if v > h._raw_thresh[i]:
                h._raw_thresh[i] = v
        time.sleep(interval)

    h.thresh = [x*calib_gain for x in h._raw_thresh]
    h.threshold = [x*calib_gain for x in h._raw_thresh]

    if h.verb:
        _ts =", ".join(["{:.2f}".format(x) for x in h.thresh])
        print "[I] post-calibration, we have thresh: ", _ts

    







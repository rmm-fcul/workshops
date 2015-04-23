#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Four CASUs, with +ve feedback from self and from remote collaborator
 (assumed to be in another arena); and -ve cross-inhibition from
 local-ish competitor (assumed to be in local arena)

However, we have (optional/configurable) asymmetry in the interactions,
and different robots have to be set up to listen than to emit.

Approx. a winner-takes all neural circuit in each arena
'''

# imports
from assisipy import casu
import loggers as loglib
import numpy as np
import argparse, os, time
import sys
import casu_utils as clib
import yaml
from time import gmtime, strftime
import time

ENABLE_SET_TEMP = True
ENABLE_SET_LEDS = False

def update_temp_wrapper(h, new_temp, ref_deviate):
    '''
    only change the temperture when we requested somehting far enough
    away that it will make a difference.  This is only to work around
    the frequency of setting new values.

    '''
    
    if abs(new_temp - h.old_temp) > ref_deviate:
        # make a new request
        h.set_temp(new_temp)
        # update the info on it
        now = time.time()
        elap = now - h.last_rq_time
        h.last_rq_time = now
        tstr = strftime("%H:%M:%S-%Z", gmtime())
        print "[I] requested new temp @{} from {:.2f} to {:.2f}".format(
                tstr, h.old_temp, new_temp)
        h.old_temp = new_temp



class Fakeobj(object):
    ''' just have an object we can add properties to'''
    def __init__(self):
        self._thing = "yo"

if __name__ == "__main__":
    #{{{ external parameters
    #parser = argparse.ArgumentParser()
    #parser.add_argument('-p', '--rtc-path', type=str, default='',
    #                    help="location of RTC files to configure CASUs",)
    #parser.add_argument('--logpath', type=str, required=True,
    #                    help="path to record output in")
    #parser.add_argument('--casu-set', type=str, required=True, choices=['north', 'south'],
    #                    help="Which set of casus")
    #parser.add_argument('-c', '--conf-file', type=str, default=None)
    ##TODO: incorporate the casu-set into conf file?
    #parser.add_argument('-v', '--verb', type=int, default=0,
    #                    help="verbosity level")
    #parser = argparse.ArgumentParser()
    #args = parser.parse_args()
    args = Fakeobj()
    args.rtc_path = ''
    args.logpath = './'
    args.verb = 1
    args.conf_file = "with-cross.conf"
    INPUT_CASU_NAME = 'casu-broken!'
    if len(sys.argv) > 1:
        INPUT_CASU_NAME = sys.argv[1]
        if INPUT_CASU_NAME.endswith('.rtc'):
            INPUT_CASU_NAME = INPUT_CASU_NAME[:-4]
    #}}}

    #{{{ set up parameters / other config
    if args.conf_file is not None:
        with open(args.conf_file, 'r') as f:
            all_conf = yaml.safe_load(f)
            _casu_conf = all_conf.get('casu_conf')
            _shared_conf = all_conf.get('shared')
    else:
        _casu_conf = {}
        _shared_conf = {}
        # fatal error?

    ### any derived parameters
    casu_conf = _casu_conf # this one stay as dict for now
    shared_conf = clib.Struct(**_shared_conf) # turn into dotted access.


    # temp setup
    shared_conf.temp_rng = shared_conf.max_temp - shared_conf.min_temp
    shared_conf.temp_resolution = shared_conf.temp_rng / shared_conf.max_steps

    # timing of update
    shared_conf.rel_upd_rate = int (shared_conf.update_period /
            shared_conf.resample_period)

    print "## funamental config:"
    for k in 'cross_inhib', 'remote_excit':
        print "\t{} : {}".format(k, shared_conf.get(k))
    # display.

    #cmap = clib.gen_cmap()
    cmap_fake = np.linspace(0, 1, num=8)
    #}}}

    #{{{ set up the casu objects / handles
    heaters = []
    loggers = []
    init_upd_time = time.time()
    _logtime= strftime("%H:%M:%S-%Z", gmtime())
    for name in [INPUT_CASU_NAME, ] :

        fname = "{}.rtc".format(name)
        rtc   = os.path.join(args.rtc_path, fname)
        print "connecting to casu {} ('{}')".format(name, rtc)
        # connect to the casu and set up extra properties
        h = casu.Casu(rtc_file_name=rtc, log=True)
        # identify the logical/physical mapping to neighbours. # ONLY REQD UNTIL # PR#12 merged
        h.comm_links = clib.find_comms_mapping(
            name, rtc_path=args.rtc_path, suffix='', verb=True)
        # basic params, from setup file
        h._thename    = name
        h._listento   = casu_conf[name]['listen']
        h._sendto     = casu_conf[name]['sendto']
        h.self_bias   = casu_conf[name]['self_bias']
        h.friend_bias = casu_conf[name]['friend_bias']
        h.enemy_bias  = casu_conf[name]['enemy_bias']
        h.verb        = args.verb
        h.max_steps   = float(shared_conf.max_steps)
        h.sat_lim     = shared_conf.sat_lim
        h.threshold   = 7*[0]

        # memory/states, counters
        h.detect_data = np.zeros(shared_conf.hist_len,)
        h.last_update_time = init_upd_time
        h.prev_temp   = shared_conf.min_temp
        h.enemy_most_recent_val  = 0
        h.friend_most_recent_val = 0
        h.enemy_rx   = 0 # debug: count balance of msgs recv from each neighbor
        h.friend_rx  = 0 # ditto
        h.err_cnt    = 0 # this just keeps track of windowed vs inst IR counts

        h.old_temp   = 25 
        h.last_rq_time = time.time()

        heaters.append(h)
        # connect each one to a logger
        logfile = '{}/{}-{}.log'.format(args.logpath, name, _logtime)
        logger = loglib.LogCASUActivity(h, logfile, append=False, delimiter=';')
        loggers.append(logger)
    #}}}
    # run calibration
    for h in heaters:
        clib._calibrate(h, calib_steps=50, calib_gain=1.1, interval=0.1)
        # and RECORD THE VALUES!
        calib_file = '{}/{}-{}.calib'.format(args.logpath, name, _logtime)
        with open(calib_file, 'w') as f:
            _ts ="; ".join(["{:}".format(x) for x in h.threshold])
            f.write(_ts + "\n")
            print "[I] post-calibration, we have thresh: ", _ts

    try:
        #{{{ main runtime controller behaviour
        ts = 0 # keep track of iterations round this loop
        while True:
            any_updates = False # used for emitting debug output
            ts += 1
            for h, logger in zip(heaters, loggers):
                now = time.time()
                elap = now - init_upd_time

                #{{{ measure inst proximity, compute l/t average
                sat_meas_count = clib.detect_bee_proximity_saturated(h)

                # compute an average recent detection value. (note: bound by ts)
                valid = min(ts, shared_conf.avg_hist_len)
                vd = np.array(h.detect_data[0:valid])
                rd = np.array(h.detect_data[0:valid]) # keep one unclipped
                vd[vd > h.sat_lim] = h.sat_lim # clip for analysis
                r_mean = vd.mean()
                r_med = np.median(vd)
                r_max = vd.max()
                #}}}

                #{{{ check for messages from neighbours
                # recv neighbouring Bee estimate/IR count
                # - use neighbouring value only if there is a neighbour
                if h._listento is not None:
                    msgs = clib.recv_all_msgs(h)
                    if h.verb >1 : print "[I] {} received {} msgs:".format(h._thename, len(msgs))

                    for src_phys, val in msgs:
                        if src_phys in h.comm_links:
                            apdx_str = "(unknown)"
                            if h.comm_links[src_phys] == "accomplice":
                                h.friend_rx += 1
                                apdx_str = "F({})".format(h.friend_rx)
                                h.friend_most_recent_val = val

                            elif h.comm_links[src_phys] == "enemy":
                                h.enemy_rx += 1
                                h.enemy_most_recent_val = val
                                apdx_str = "E({})".format(h.enemy_rx)

                        if h.verb > 1: print ("  [I] recv message from '{}'"
                                " => logical neighbor '{:12}'. Msg:{}|{}").format(
                            src_phys, h.comm_links[src_phys], val, apdx_str)
                #}}}

                #{{{ compute new temperature
                # NONLINEAR COMBINATION. Also with smoother data
                excit_total = h.self_bias * r_mean
                if shared_conf.remote_excit:
                    excit_total = (h.self_bias * r_mean +
                            h.friend_bias * h.friend_most_recent_val)

                lc = excit_total / float(h.sat_lim) # normalised
                local_contrib = shared_conf.temp_rng * lc

                rbc2 = h.enemy_most_recent_val / float(h.sat_lim)
                remote_contrib = h.sat_lim * rbc2 * h.enemy_bias

                if shared_conf.cross_inhib:
                    new_temp = shared_conf.min_temp + local_contrib - remote_contrib
                else:
                    new_temp = shared_conf.min_temp + local_contrib

                # for display, generate a summary message
                contrib_str = ("L|C|R IR[{:{fmtIR}}|{:{fmtIR}}|{:{fmtIR}}]"
                               " T[{:{fmtT}}|{:{fmtT}}|{:{fmtT}}] ").format(
                        r_mean, h.friend_most_recent_val, rbc2,
                        h.self_bias * r_mean,
                        h.friend_bias * h.friend_most_recent_val,
                        -remote_contrib,
                        fmtIR=".1f", fmtT="+.1f"
                        )
                # an appendix to message (re temp)
                contrib_str += "{:.1f}+{:.1f} => {} {:.1f}{}".format(shared_conf.min_temp,
                        new_temp-shared_conf.min_temp, clib.BLU, new_temp, clib.ENDC)

                # protect / clip temperature value
                new_temp = sorted([shared_conf.min_temp, new_temp, shared_conf.max_temp])[1]
                #}}}

                #{{{ do we need to update setpoint this iteration?
                update_temp_now = False
                if now - h.last_update_time > shared_conf.update_period:
                    update_temp_now = True # this casu
                    any_updates = True     # shared flag for all casus (disp)
                #}}}

                # set color, based on target and current temp (always update clr)
                t_cur = clib.find_mean_ext_temp(h)
                r,g,b = clib.gen_clr_tgt(
                    h.prev_temp, cmap_fake, t_cur, min_temp=shared_conf.min_temp,
                    max_temp=shared_conf.max_temp)
                r = rd.mean() / 6.0
                #new_temp = shared_conf.min_temp + local_contrib - remote_contrib
                #

                if ENABLE_SET_LEDS:
                    # this is a small validation to check we have inter-comms ok

                    pos = h.self_bias * r_mean
                    neg = h.enemy_bias * rbc2
                    _test_x = pos - neg

                    if _test_x > 0: r,g,b = (1,0,1) # PURPLE
                    if _test_x > 1: r,g,b = (0,0,1) # B;IE
                    if _test_x > 2: r,g,b = (0,1,0) # GREEN
                    if _test_x > 3: r,g,b = (1,1,0) # YELLOW
                    if _test_x > 4: r,g,b = (1,0.6,0) # orange
                    if _test_x > 5: r,g,b = (1,0,0) # red
                    print "test_val: {:.2f}; rgb=".format(_test_x), r,g,b
                    h.set_diagnostic_led_rgb(r=r,g=g,b=b)

                if (update_temp_now):
                #{{{ if so, change temperature and LED display clr
                    if ENABLE_SET_TEMP:
                        update_temp_wrapper(h, new_temp, ref_deviate=0.5)


                    h.prev_temp = new_temp
                    h.last_update_time = time.time()

                    #{{{ diagnostic messages to cmdline
                    # a bit of diagnostics on the colouring
                    print "[ts={} ({:.0f}m{:.0f}s)] {}: {}T=>{:.2f} {}(T_cur={:.2f}), ".format(
                        ts, (ts*shared_conf.resample_period)/60, (ts * shared_conf.resample_period) % 60, h._thename, clib.BLU, new_temp, clib.ENDC, t_cur,
                    )

                    # some info on the (mis)match between the instantaneous reading and the
                    # time-averaged version. [CLIPPED DATA]
                    print "\tinst: {}, mean|med|max recent: {:.2f}|{:.2f}|{:.2f}".format(
                        sat_meas_count, r_mean, r_med, r_max), #vd,
                    err = np.abs(sat_meas_count - r_mean)
                    if err > 0.5:
                        h.err_cnt += 1
                        print clib.ERR + "[W] {:.2f} away ({}|{} errs)".format(err, h.err_cnt, ts/shared_conf.rel_upd_rate) + clib.ENDC,
                    print " [LED{:.2f}]".format(r)

                    # (mis)match between instantaneous and time-average [UNCLIPPED]
                    print "\tinst: {}, mean|med|max recent: {:.2f}|{:.2f}|{:.2f}".format(
                        int(rd[0]), rd.mean(), np.median(rd), rd.max()), #rd,
                    err = np.abs(rd[0] - rd.mean())
                    if err > 0.5:
                        print clib.ERR + "[W] {:.2f} away ({}|{} errs)".format(err, "?", ts/shared_conf.rel_upd_rate) + clib.ENDC,
                    # decomposition of contributions
                    print "\n\t" + contrib_str
                    #}}}
                #}}}

                # transmit my count -- if have neigbours, always send.
                for neigh in h._sendto: #(send time-averaged, saturated value
                    clib.transmit_my_count( h, "{:.3f}".format(r_mean), neigh);

                #{{{ make a log entry
                # - includes the counts made as well as basic sensor measrements
                extra_recs = [sat_meas_count , h.friend_most_recent_val,
                              h.enemy_most_recent_val, new_temp, rd[0], rd.mean()]
                extra_string = ";".join([str(x) for x in extra_recs])
                logger.record_sensors(suffix=extra_string)
                #}}}

            # sleep between updating all N casus
            if any_updates: clib.sep_with_nowtime()
            time.sleep(shared_conf.resample_period)
        #}}}

    except KeyboardInterrupt:
        #{{{ cleanup
        print "closing down CASUs..."
        for h in heaters:
            h.stop()
        for l in loggers:
            l._cleanup()

        #}}}


#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
controlling of the bees, implementing BEECLUST behaviour that is sensitive to
heat in environment (and social interaction).

'''

from time import sleep
import time, datetime
import random, argparse, os, sys
import yaml
from assisipy import bee
import bee_log
import signal
from math import sin, cos, pi
import numpy as np

#{{{ math convenience
def deg2rad(x):
    '''
    convert an angle in degrees to an angle in radians. Pure python
    implementation as per the numpy docs. (scalar only - not vectorised)
    '''
    return x * (pi / 180.0)

def rad2deg(x):
    '''
    convert an angle in radians to an angle in degrees. Pure python
    implementation as per the numpy docs. (scalar only - not vectorised)
    '''
    return x * (180.0 / pi)
#}}}


#{{{ basic bee behaviours
CW = +1
CCW = -1
IMMEDIATE_FWD = False
START_STATE_FWD = True
DETECT_SLIDE = True

def stop(abee):
    vel = 0.0 # cm/s  - real mean vel = 1.25
    abee.set_vel(vel, vel) # speed of L/R wheels

def go_straight(abee):
    vel = 2.25 # cm/s  - real mean vel = 1.25
    abee.set_vel(vel, vel) # speed of L/R wheels

def turn_random(abee):
    vel = 0.4 # cm/s
    direction = random.choice([-1,1]) # pick a sign of velocity
    abee.set_vel(vel * direction, -1 * vel * direction)
    #sleep(random.uniform(1,5))
    sleep(random.uniform(0.5,2))

def measure_heat(abee):
    ''' measure the temperature in current position '''
    temp = abee.get_temp()
    return temp
#}}}

#{{{ waiting time functions
def compute_wait_hill(temp,
        a=   3.090475362,
        b=   -0.0402754316,
        c=   -28.4570871346,
        d=   1.7850341689,
        e=   22.4490966476,
        f=   0.6451864513,
        ):
    '''
    compute waiting time for bee according to temperature, based on experimental data
    from Graz lab
    =((a+b*D5)^c_/((a+b*D5)^c_+d^c_))*e+f

    Hill function, fitted for range 0..44

    '''
    temp = float(temp)

    waiting_time = ((a+b*temp)**c/((a+b*temp)**c+d**c))*e+f
    #waiting_time = ( \
    #        (a + b * temp) ** c /( (a + b * temp) **c + d**c ) \
    #        ) * e + f

    return waiting_time

def test_compute_wait_hill(x):
    #x = range(28, 38)
    #x = range(8, 43)
    w = [ compute_wait_hill(_w) for _w in x]

    import matplotlib.pyplot as plt
    plt.figure(1); plt.clf()
    plt.plot(x, w)
    plt.xlabel('temperature ($^\circ$C)')
    plt.ylabel('waiting time (s)')
    plt.show()
#}}}

#{{{ collisions test
def check_for_collision(abee, range_thresh=1000, verb=False):
    '''
    does this bee have an object in front of it?
    We use the front three sensors
    '''

    collision = False
    objs = []
    ranges = []
    # inspect all sensors of interest
    #['Bee', 'Casu', 'Physical', 'None'] # these are the outputs from objet types
    sensors = [bee.OBJECT_LEFT_FRONT, bee.OBJECT_FRONT, bee.OBJECT_RIGHT_FRONT,]
            #bee.OBJECT_SIDE_RIGHT, bee.OBJECT_SIDE_LEFT,
    for sensor in sensors:
        (o, r) = abee.get_object_with_range(sensor)
        if verb:
            print "{4} Bee has detected object '{1}' on sensor {0} at range {2:.2f} ({3})".format(
                sensor, o, r, r < range_thresh, '* ' if r < range_thresh else '  ')

        if (o is not 'None'):
            if r < range_thresh:
                collision = True
                objs.append(o)
                ranges.append(r)

    triggered_sensor_directions = 0
    for r in ranges:
        if r < range_thresh:
            triggered_sensor_directions += 1
    if len(sensors) - triggered_sensor_directions < 2:
        collision = True
    else:
        collision = False

    # how do they vote? we assume if any of them hit, we have a collision.
    # new implementation choice:
    # if there are not at least two sensors with spaces, we rotate.
    # - or rather, we define there to have been a collision detected
    # - that means that the ext behaviour choice is contingent on a different
    #   voting rule now.

    return collision, objs, ranges


def check_directional_collision(abee, range_thresh=None):
    '''
    use specific direction sensors to determine an action as appropriate
    # - if there is a bee in any sensor, halt/compute waiting time & wait
    # - else, take aversive action according to strength of l or r sensors.
    '''
    # measure ranges and object types
    o_l, r_l = abee.get_object_with_range(bee.OBJECT_LEFT_FRONT)
    o_f, r_f = abee.get_object_with_range(bee.OBJECT_FRONT)
    o_r, r_r = abee.get_object_with_range(bee.OBJECT_RIGHT_FRONT)

    bee_nearby = False
    rotate_dir = None
    if ((o_l == 'Bee' and r_l < range_thresh) or (o_f == 'Bee' and r_f < range_thresh) or (  o_r == 'Bee' and r_r < range_thresh) ):
         bee_nearby = True

    else:
        if r_f < range_thresh:
            # note: if there is room straight ahead, then we can ignore
            # the fact that the peripheral sensors are firing (or not)
            if r_r < r_l:
                # if object to right is closer, rotate left
                rotate_dir = CCW
            else:
                # left must be closer, so rotate right
                rotate_dir = CW

    return bee_nearby, rotate_dir


def check_for_collision_with_bees(objs, ranges, range_thresh=None):
    '''
    check whether any of the possible objects we are close to are bees.
    if the range_thresh is set, then only pay attention to objects that are
    closer than this value.
    Otherwise assume that the previous test filtered sufficiently

    '''

    bee_nearby = False
    for o, r in zip(objs, ranges):
        if o in ['Bee']:
            if range_thresh is not None:
                if r < range_thresh:
                    bee_nearby = True
            else:
                bee_nearby = True
            if (0): print "{2}Detected a bee ('{0}') at range {1:.2f} ".format(o, r,
                    '**' if bee_nearby else '  ')
    return bee_nearby


#}}}


#{{{ BeeClustBee
class BeeClustBee(object):
    '''
    implementation of the behavoural model BeeClust as per Schmickl 2008.
    using Enki/assisipy bee interface.
    '''
    #{{{ initialiser
    def __init__(self, bee_name, logfile, pub_addr, sub_addr, conf_file=None,
                 verb=False):
        self.bee_name = bee_name
        if conf_file is not None:
            with open(conf_file, 'r') as f:
                conf = yaml.safe_load(f)
        else:
            conf = {}

        '''instantiates a assisipy.bee object but not derived from bee (At present)
        # default settings are 2nd argument, if not set by config file
        '''
        # cm - how close is a detected object considered a collision?
        self.range_thresh_any_collision = conf.get('range_thresh_any_collision', 0.5)
        self.override_fwd_clr           = conf.get('override_fwd_clr', False)
        self._fwd_clr                   = conf.get('fwd_clr', (0.3,0.3,0.3))
        self.update_delay               = conf.get('update_interval', 0.1)
        self.slide_det_len = 3
        self.slide_yaw_tol = deg2rad(5)

        self.range_thresh_bee = 0.5
        self.verb = verb

        print "attempting to connect to bee with name %s" % bee_name
        print "\tpub_addr:{}".format(pub_addr)
        print "\tsub_addr:{}".format(sub_addr)
        self.mybee = bee.Bee(name=self.bee_name, pub_addr=pub_addr,
                             sub_addr=sub_addr)
        self.counter = 0
        self.logger = bee_log.LogBeeActivity(bee_to_log=self.mybee,
                logfile=logfile, append=False)

        #self.CLR_FWD  = {'r':0.93,'g':0.79,'b'r:0}
        #self.CLR_WAIT = {'r':0.93,'g':0.0, 'b'r:0}
        self.CLR_FWD  = (0.93, 0.79, 0)
        self.CLR_COLL_OBJ  = (0, 0, 1)
        self.CLR_COLL_BEE  = (0, 1, 0)
        self.CLR_WAIT  = (0.93, 0.0, 0)
        self._xhist   = np.zeros(self.slide_det_len,)
        self._yhist   = np.zeros(self.slide_det_len,)
        self._yawhist = np.zeros(self.slide_det_len,)


        if self.override_fwd_clr:
            # special color for this machine / bee
            c = [float(n) for  n in self._fwd_clr.strip('()').split(',')]
            self.CLR_FWD = c
            #print "[I] custom color for bee %s" % bee_name,  self.CLR_FWD, len(self.CLR_FWD)
            #self.CLR_FWD = (0.0, 0.60, 0.80)


    #}}}
    #{{{ detect_sliding
    def detect_sliding(self):
        '''
        return true if have been sliding, where bearing does not get honoured
        '''
        sliding = False
        x, y, yaw = self.mybee.get_true_pose()
        # step all data back by one
        self._xhist   = np.roll(self._xhist, 1)
        self._yhist   = np.roll(self._yhist, 1)
        self._yawhist = np.roll(self._yawhist, 1)
        # enter new recordings
        self._xhist[0]   = x
        self._yhist[0]   = y
        self._yawhist[0] = yaw

        
        # for VERTICAL walls, these are heading at pi/2 or -pi/2
        #0.75 * np.sin(np.deg2rad(5))
        if (abs(yaw - pi/2.0) > self.slide_yaw_tol or
                abs(yaw - (3.0*pi)/2.0) > self.slide_yaw_tol):
            # what is x movement?
            d = []
            for i in xrange(len(self._xhist) - 1):
                d.append(self._xhist[i] - self._xhist[i+1])

            mean_xmov = np.mean(np.abs(d))


            #print "[I] cehcking for V  slide with truepos: {:.2f}, {:.2f}, {:.2f} (move: {:.2f}".format( x,y, np.rad2deg(yaw), mean_xmov),
            if mean_xmov < (0.05 * np.sin(np.deg2rad(5))):
                sliding = True
                #print "AN I THINK I AM"
            #else: print "(not slide)"

        # for HIRIIZONTAL walls, these are 0 or pi
        '''
        UNTESTED -- for initial test we use the vert walls
        elif (abs(yaw - pi) > self.slide_yaw_tol or
                abs(yaw - 0) > self.slide_yaw_tol):
            # what is y movement?
            d = []
            for i in xrange(len(self._yhist) - 1):
                d.append(self._yhist[i] - self._yhist[i+1])
            mean_ymov = np.mean(np.abs(d))

            if mean_ymov < (0.05 * np.sin(np.deg2rad(5))):
                sliding = True
        '''



        
        return sliding
    #}}}

    def stop(self):
        self.mybee.set_color(r=0.25, g=0.25, b=0.25)
        stop(self.mybee)

    def behav_loop_new(self):
        '''
        explicit object aversion
        '''
        #{{{ beeclust model loop
        if not START_STATE_FWD:
            turn_random(self.mybee) # in case the bee got stuck on wall at init time?
        while True:
            self.logger.record_pos() # maybe better at end?
            sleep(self.update_delay) # no more than 10x /sec updates

            # test for collision
            bee_nearby, rotate_dir = check_directional_collision(self.mybee, range_thresh=self.range_thresh_any_collision)

            if not bee_nearby:
                if rotate_dir is None:
                    # carry on
                    self.mybee.set_color(*self.CLR_FWD)
                    #set_color(self,r=0.93,g=0.79,b=0)
                    if DETECT_SLIDE:
                        #am_i_sliding = self.detect_sliding()
                        if self.detect_sliding():
                            self.mybee.set_color(*self.CLR_COLL_OBJ)
                            turn_random(self.mybee)

                    self.mybee.set_color(*self.CLR_FWD)
                    go_straight(self.mybee)
                else:
                    self.mybee.set_color(*self.CLR_COLL_OBJ)
                    # we could use the direction as given CCW/CW, but here
                    # we simply randomly choose a direction
                    turn_random(self.mybee)
                    # once rotated for a random time, continue forwards
                    if IMMEDIATE_FWD:
                        go_straight(self.mybee)
            else:
                self.mybee.set_color(self.CLR_COLL_BEE)
                # we are near another bee. So make a heat measurement of the env
                current_temp = measure_heat(self.mybee)
                # and then compute a waiting time, according to preference
                waiting_time = 1.0 * compute_wait_hill(current_temp)
                if self.verb : print "{4} Detected bee@{2:.1f}{3:.1f}; curent temp is {0:.3f}->waiting time {1:.2f} ".format(
                        current_temp, waiting_time,
                        self.mybee.get_true_pose()[0], self.mybee.get_true_pose()[1],
                        self.bee_name, )

                # finally, wait that amount of time before turning
                stop(self.mybee)
                wait_max = 25.0

                self.mybee.set_color(g=0.35+0.65*(waiting_time/wait_max))#, g=0.0, b=0)
                sleep(waiting_time)

                # after waiting we randomly turn and then return to forward behav
                turn_random(self.mybee)
                if IMMEDIATE_FWD:
                    go_straight(self.mybee)

        #}}}

#}}}

# clean exiting

#def _cleanup(signum, frame):
#    pass
#def goodbye(name, adjective):
#        print 'Goodbye, %s, it was %s to meet you.' % (name, adjective)

import atexit
        #atexit.register(goodbye, 'Donny', 'nice')

        # or:


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--logpath', type=str, required=True,
                        help="path to record output in")
    parser.add_argument('-bn', '--bee-name', type=str, default='BEE',
                        help="name of the bee to attach to")
    parser.add_argument('-pa', '--pub-addr', type=str, default='tcp://127.0.0.1:5556',
                        help="publish address (wherever the enki server listens for commands)")
    parser.add_argument('-sa', '--sub-addr', type=str, default='tcp://127.0.0.1:5555',
                        help="subscribe address (wherever the enki server emits commands)")
    parser.add_argument('-c', '--conf-file', type=str, default=None)
    parser.add_argument('-v', '--verb', action='store_true', help="be verbose")

    args = parser.parse_args()

    random.seed()
    logfile = os.path.join(args.logpath, "bee_track-{}.csv".format(args.bee_name))
    the_bee = BeeClustBee(
        bee_name=args.bee_name, logfile = logfile,
        pub_addr=args.pub_addr, sub_addr=args.sub_addr,
        conf_file=args.conf_file,
        verb=args.verb,
    )
    #atexit.register(goodbye, adjective='nice', name='Donny')
    # now that we have created the object that we want to write at cleanup,
    # maybe do a nested func?

    #def _cleanup(logger_handle):
    #    #print "Finished at:",  datetime.datetime.fromtimestamp(time.time())
    def cleanup_hdl(signum, frame):
        print "i'm exiting on signal {} but writign logfile {} first".format(
            signum, the_bee.logger.logfile.name)

        s = "# *** SIG - {} Finished at: {}".format(
            signum,
            datetime.datetime.fromtimestamp(time.time()))
        the_bee.stop()
        the_bee.logger.logfile.write(s + "\n")
        the_bee.logger.logfile.close()
        # we handled it gracefully?
        sys.exit(0)
        pass


    #atexit.register(_cleanup, logger_handle=the_bee.logger)
    # catch reawonalbe signals. (note: -9 SIGKILL is uncatchable..)
    signal.signal(signal.SIGINT, cleanup_hdl)  # ctrl-c, #2
    signal.signal(signal.SIGTERM, cleanup_hdl) # 15.
    signal.signal(signal.SIGQUIT, cleanup_hdl) # 3
    # now launch the infinite loo
    try:
        #print "PID: ", os.getpid()
        while True:
            the_bee.behav_loop_new()
    except KeyboardInterrupt:
        print "shutting down bee {}".format(args.bee_name)
        pass

    # DOES THIS BIT get executed? or do we need cleanup to be within the except?
    # with SIGINT (-2) it does get executed; with SIGTERM (-15) or SIGKILL (-9)
    # the try/except fails to catch it and exits straight away.

    #the_bee.logger._cleanup()


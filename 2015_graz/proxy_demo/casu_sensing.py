#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
When a bee approaches, start flashing
show closeness with intensity of flashing
and #sensors with color

RM - april 2015 workshop.
'''

from assisipy import casu
import time
import sys

class CasuController(object):

    def __init__(self, rtc_file, calib_steps=50, interval=0.1, verb=False):
        self.verb = verb
        self.interval = interval
        self.calib_gain = 1.1
        # connect to CASU
        self.__casu = casu.Casu(rtc_file, log=True)
        # calibrate sensor levels
        self._calibrate(calib_steps)

    def stop(self):
        self.__casu.stop()



    def _calibrate(self, calib_steps):
        '''
        read the sensors several times, and take the highest reading
        seen as the threshold.
        '''
        self._raw_thresh = [0] * 7 # default cases for threshold
        for stp in xrange(calib_steps):
            for i, v in enumerate(self.__casu.get_ir_raw_value(casu.ARRAY)):
                if v > self._raw_thresh[i]:
                    self._raw_thresh[i] = v
            time.sleep(self.interval)

        self.thresh = [x*self.calib_gain for x in self._raw_thresh]

        if self.verb:
            _ts =", ".join(["{:.2f}".format(x) for x in self.thresh])
            print "[I] post-calibration, we have thresh: ", _ts

    def detection_loop(self):
        '''
        one step of the detection loop for IR sensing etc

        '''
        # 1. read sensors
        # 2. test which are above threshold
        # 3a. count sensors 0:3 -> red channel
        # 3b. count sensors 4:6 -> green channel
        # (variant: 3. count sensors 0:6 -> red channel)
        # 4. set diagnostic LED following (3).
        # 5. delay for 0.5 * interval
        # 6. turn off LED
        # 7. delay for 0.5 * interval


        # 1. read sensors
        raw_values = self.__casu.get_ir_raw_value(casu.ARRAY)

        # 2. test which are above threshold
        above_thr = [ int(rv>tr) for tr, rv in zip(self.thresh, raw_values)]

        # 3a. count sensors 0:3 -> red channel
        # 3b. count sensors 4:6 -> green channel
        # (variant: 3. count sensors 0:6 -> red channel)
        r = sum(above_thr[0:3])
        g = sum(above_thr[3:6]) 
        
        # set as a range \in off..on
        # - with >1 color channel, this is not very noticable in the physical LEDs
        #if r > 0: r  = 0.25 + 0.75*r/3.0
        #if g > 0: g  = 0.25 + 0.75*g/3.0
        if self.verb:
            print "[I] r,g,b={}, {}, {}".format(r,g,0)

        # 4. set diagnostic LED following (3).
        self.__casu.set_diagnostic_led_rgb(g=g, r=r, b=0)

        # 5. delay for 0.5 * interval
        time.sleep(self.interval * 0.5)
        # 6. turn off LED
        self.__casu.set_diagnostic_led_rgb(0,0,0)
        # 7. delay for 0.5 * interval (before next sampling)
        time.sleep(self.interval * 0.5)



if __name__ == '__main__':
    casu_rtc_file = sys.argv[1] # this is supplied by the deploy tool
    interval = 1.0 / 5
    ctrl = CasuController(casu_rtc_file, verb=True, interval=interval)
    init_time = time.time()
    try:
        while True:
            ctrl.detection_loop()
            elap = time.time() - init_time
            if int(elap) % 10 == 0:
                print "[] time is {}".format(int(elap))
    except KeyboardInterrupt:
        print "[I] done, shutting down"
        
    ctrl.stop()



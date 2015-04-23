'''
classes and utilities to aid with logging bee behaviour from enki
'''
import os
import sys
import time, datetime
import random
from math import pi

#{{{ logging
class LogBeeActivity(object):
    def __init__(self, bee_to_log, logfile, append=True):
        '''
        class to write logs for the bee activity through a simulation.
        The records will be made in a non-evenly spaced way since there
        are many different delays through the control loop
        '''
        self.bee = bee_to_log
        mode = 'a' if append else 'w'
        self.LINE_END = "\n"
        try:
            self.logfile = open(logfile, mode)
        except FileException:
            print "[F] cannot open logfile"
            raise


    def record_pos(self, suffix=''):
        '''
        consistently write output for a given recording step
        timestamp, pos(x), pos(y), yaw, temperature, 
        '''
        fields = []
        t = time.time()
        #print "Finished at:",  datetime.datetime.fromtimestamp(time.time())
        fields.append(t)
        fields.extend(self.bee.get_true_pose()) # three floats returned
        fields.append(self.bee.get_temp())
        # because times have many SF, we print the data for all fields in full
        #print len(fields), fields
        s = ";".join([str(f) for f in fields])
        if len(suffix):
            s += ";" + suffix
        s += self.LINE_END
        self.logfile.write(s)


        pass
    def _cleanup(self):
        self.logfile.close()
        print "closed logfile"
        pass

class FakeBee(object):
    ''' a fake bee that generates random results with same interface as 
    the assisipy bees'''
    def __init__(self, name):
        self.name = name
    def get_true_pose(self):
        x   = random.uniform(-10, 10)
        y   = random.uniform(-10, 10)
        yaw = random.uniform(-pi, pi)
        return (x, y, yaw)

    def get_temp(self):
        t = random.uniform(20,45)
        return t
        

def test_logger():
    mybee = FakeBee('goat1')
    logger = LogBeeActivity(mybee, "/tmp/log.csv", False)
    
    for i in xrange(23):
        logger.record_pos()
        time.sleep(random.uniform(0.3, 2))

    logger._cleanup() # want this to happen by just deleting the obejct..


if __name__ == '__main__':
    test_logger()



#}}}


'''
classes and utilities to aid with logging bee behaviour from enki
'''
import os
import time
import random
from math import pi

#{{{ logging bees
class LogBeeActivity(object):
    def __init__(self, bee_to_log, logfile, append=True, delimiter=';'):
        '''
        class to write logs for the bee activity through a simulation.
        The records will be made in a non-evenly spaced way since there
        are many different delays through the control loop
        '''
        self.bee = bee_to_log
        mode = 'a' if append else 'w'
        self.LINE_END = os.linesep # platform-independent line endings
        self._delimeter = delimiter
        try:
            self.logfile = open(logfile, mode)
        except IOError as e:
            print "[F] cannot open logfile ({})".format(e)
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
        s = self._delimeter.join([str(f) for f in fields])
        if len(suffix):
            s += self._delimeter + suffix
            #s += ";" + suffix
        s += self.LINE_END
        self.logfile.write(s)

    def _cleanup(self):
        self.logfile.close()
        print "closed logfile"

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


def test_bee_logger():
    ''' show basic use case of the bee logger'''
    mybee = FakeBee('goat1')
    logger = LogBeeActivity(mybee, "/tmp/log.csv", False, delimiter=',')

    for _ in xrange(23):
        logger.record_pos()
        time.sleep(random.uniform(0.3, 2))

    logger._cleanup() # want this to happen by just deleting the obejct..




#}}}

#{{{ logging CASUs
#{{{ LogCASUActivity
class LogCASUActivity(object):
    def __init__(self, casu_to_log, logfile, append=True, delimiter=';'):
        '''
        class to write logs for the CASU activity through a simulation.
        The records will be made in a non-evenly spaced way since there
        are many different delays through the control loop -- indeed, it
        is totally possible to have event-driven behaviour

        What does this log?
        v1.0: timestamp, temp of sensors [N,E,S,W,int], IR sensors [0..5]
        '''
        self.version = 1.0
        self.casu = casu_to_log
        mode = 'a' if append else 'w'
        self.LINE_END = os.linesep # platform-independent line endings
        self._delimeter = delimiter
        self._logfile_name = logfile
        try:
            self.logfile = open(logfile, mode)
        except IOError as e:
            print "[F] cannot open logfile ({})".format(e)
            raise

    def get_all_casu_temps(self):
        ''' convenience method to get all temps.'''
        # should this actually be in the logger rather than the
        # fake casu? downside this now depends on importing
        # assispy.casu
        TEMP_SENSOR_ID_LIST = [8, 9, 10, 11, 12]
        t = [self.casu.get_temp(sensor) for
             sensor in TEMP_SENSOR_ID_LIST]
        return t

    def record_sensors(self, suffix=''):
        '''
        consistently write output for a given recording step
        timestamp, sensor temps [NESW I], sensor readings[1..6]
        '''
        IR_ARRAY = 10000
        fields = []
        t = time.time()
        #print "Finished at:",  datetime.datetime.fromtimestamp(time.time())
        fields.append(t)
        fields.extend(self.get_all_casu_temps()) # 5 floats
        #fields.extend(self.casu.get_ir_raw_value(self.casu.IR_ARRAY)) # 6 floats
        fields.extend(self.casu.get_ir_raw_value(IR_ARRAY)) # 6 floats
        # because times have many SF, we print the data for all fields in full
        #print len(fields), fields
        s = self._delimeter.join([str(f) for f in fields])
        if len(suffix):
            s += self._delimeter + suffix
            #s += ";" + suffix
        s += self.LINE_END
        self.logfile.write(s)

    def _cleanup(self):
        self.logfile.close()
        print "[I] LogCASUActivity - closed logfile '{}'".format(
            self._logfile_name)
#}}}

#{{{ fake casu
class FakeCASU(object):
    ''' a fake casu that generates random results with same interface as
    the assisipy casus'''
    def __init__(self, name):
        self.name = name

        self.IR_SENSORS = {
            'IR_N' :0,
            'IR_NE':1,
            'IR_SW':2,
            'IR_S' :3,
            'IR_SE':4,
            'IR_NW':5,
        }
        # should these be ordered dicts?
        self.temp_sensors = {
            'TEMP_N'  :0,
            'TEMP_E'  :1,
            'TEMP_S'  :2,
            'TEMP_W'  :3,
            'TEMP_TOP':4,
        }

        self.IR_SENSOR_MAP = {v: k for k, v in self.IR_SENSORS.iteritems()}
        self.IR_IGNORED = 0 #<F4
        self.IR_ARRAY = 10000 # same value as from assisipy.casu
        self.TEMP_ARRAY = 10000

    def _get_all_ir_values(self):
        ''' return an array for all of the IR values '''
        # turns out just passing in casu.ARRAY gets you all IR readings
        raw_irs = [self.get_ir_raw_value(sensor) for
                   sensor in self.IR_SENSORS.values()]
        return raw_irs

    def get_ir_raw_value(self, sensor=0):
        ''' make up an IR value '''
        if sensor == self.IR_ARRAY:
            vals = [ random.uniform(0,100) for _ in xrange(len(self.IR_SENSORS))]
        else:
            vals = random.uniform(0,100)

        return vals

    def _get_all_temps(self):
        ''' convenience method to get all temps.'''
        # should this actually be in the logger rather than the
        # fake casu?
        t = [self.get_temp(sensor) for
             sensor in self.temp_sensors.values()]
        return t

    def get_temp(self, sensor=0):
        ''' make up a temp for the given temp sensor '''
        # note: I've invented an array return func, which is probably
        # bad practice since it doesn't yet exist in the API
        if sensor == self.TEMP_ARRAY:
            t = [random.uniform(20,45) for _ in xrange(len(self.temp_sensors))]
        else:
            t = random.uniform(20,45)
        return t
#}}}

def test_casu_logger():
    ''' show basic use case of the casu logger'''
    mycasu = FakeCASU('saucer')
    logger = LogCASUActivity(mycasu, "/tmp/casu_log.csv", False, delimiter=',')

    for _ in xrange(23):
        logger.record_sensors()
        time.sleep(random.uniform(0.3, 2))

    logger._cleanup() # want this to happen by just deleting the obejct..



#}}}



if __name__ == '__main__':
    test_bee_logger()

    test_casu_logger()



#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Identical wander controllers for n bees.
Taken from assisi-python/examples/bees_in_casu_array

"""
import argparse

from assisipy import bee

from math import pi, sin, cos
from random import random
import time
import threading

class BeeWander:
    """ 
    A demo bee wander controller. 
    An example of using the Bee-API.
    """

    def __init__(self, bee_name):
        self.__bee = bee.Bee(name = bee_name)
        self.__thread = threading.Thread(target=self.wander)
        self.__thread.daemon = True
        self._rotate_sz = 1.25
        self.__thread.start()

    def go_straight(self):
        #self.__bee.set_vel(0.5,0.5)
        self.__bee.set_vel(1.25, 1.25) 

    def stop(self):
        #self.__bee.set_vel(0.5,0.5)
        self.__bee.set_vel(0, 0)

    def turn_left(self):
        self.__bee.set_vel(-1.0 * self._rotate_sz, +1.0 * self._rotate_sz)

    def turn_right(self):
        self.__bee.set_vel(+1.0 * self._rotate_sz, -1.0 * self._rotate_sz)

    def wander(self):
        """ 
        Wander around and avoid obstacles. 
        """
        # first do a small rotate
        self.turn_left()
        time.sleep(0.1)
        while True:
            self.go_straight()
            rf = 1
            rdiag = 1.5
            while ((self.__bee.get_range(bee.OBJECT_FRONT) < rf)
                   and (
                       self.__bee.get_range(bee.OBJECT_RIGHT_FRONT) < rdiag or
                       self.__bee.get_range(bee.OBJECT_LEFT_FRONT) < rdiag
                       )):
                r = random()
                if r < 0.5:
                    self.turn_left()
                    time.sleep(0.2)
                else:
                    self.turn_right()
                    time.sleep(0.2)
                    
            #while ((self.__bee.get_range(bee.OBJECT_FRONT) < rf)
            #       and (self.__bee.get_range(bee.OBJECT_LEFT_FRONT) < rdiag)):
            #    self.turn_right()

            time.sleep(0.1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--num-bees', type=int, default=1,
            help='number of bees to run.')
    args = parser.parse_args()

    # Spawn the bees at randomly generated poses and let them run :)
    bees = []
    for i in range(1, args.num_bees + 1):
        if i < 10:
            bees.append(BeeWander('Bee-00{0}'.format(i)))
        else:
            bees.append(BeeWander('Bee-0{0}'.format(i)))

    print('All bees connected!')

    # Prevent the program from exiting
    try:
        while True:
            pass
    except KeyboardInterrupt:
        for b in bees:
            b.stop()
        print "done, goodbye."


        

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A simple simulation environment with one Casu and one bee.
"""

from assisipy import sim

from math import pi

if __name__ == '__main__':

    simctrl = sim.Control()

    # Spawn the Bee and the Casu
    simctrl.spawn('Casu','casu-001',(0,0,0))
    simctrl.spawn('Bee','Bee-001',(2,0,pi/2))


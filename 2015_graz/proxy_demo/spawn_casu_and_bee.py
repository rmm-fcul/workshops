#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simulation environment, with only CASUs.
We just spawn CASUs first so we can run calibration without bees present.

"""

from assisipy import sim
#import argparse

if __name__ == '__main__':
    #parser = argparse.ArgumentParser()
    #parser.add_argument('-nc', '--num-casus', type=int, default=1,
    #        help='number of casus to spawn.')
    #args = parser.parse_args()
    # for now, can't do the parsing so quicky since positions need 
    # calucating -- so just use the deploy env.

    simctrl = sim.Control()
    
    # Spawn the Casus
    simctrl.spawn('Casu','casu-001',(0,0,0))

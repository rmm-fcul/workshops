#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A simple simulation environment with one Casu and one bee.
"""

from assisipy import sim
from assisipy_simtools.arena import build_arenas, enki_ctrl, enki_prep
from assisipy_simtools.arena.transforms import Transformation, apply_transform_to_group
from random import random
from math import pi, cos, sin
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--num-bees', type=int, default=1,
            help='number of bees to run.')
    #parser.add_argument('-r', '--radius', type=float, default=15.0,
    #        help='radius of circular arena')
    args = parser.parse_args()

    # generate a simple arena
    T1 = Transformation(5, 0, pi/2)
    arena1, a_bounds = build_arenas.gen_base_arena(
            length=16.5, width=7.5, ww=0.5, arc_steps=17)
    arena_placed = apply_transform_to_group(arena1, T1)

    simctrl = sim.Control()
    
    # Spawn each of the bees 
    if 0:
      for i in range(1, args.num_bees + 1):
        rr = args.radius / 2.0
        r = (rr-1.5-0.5) * random()
        r += 1.5 # don't spawn on top of the casu
        theta = 2 * pi * random()
        x = r * sin(theta)
        y = r * cos(theta)
        name = 'Bee-00{0}'.format(i)
        simctrl.spawn('Bee', name, (x, y, theta))

    # spawn the walls
    enki_prep.spawn_poly_group( simctrl, arena_placed, (0,0,0), label_stub='arena',
            color=(0.5,0.5,0.5), verb=1)


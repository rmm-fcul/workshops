#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A simple simulation environment with one Casu and one bee.
"""

from assisipy import sim
from assisipy_simtools.arena import build_arenas, enki_ctrl

from math import pi

if __name__ == '__main__':
    sz = 10.0

    # generate a simple arena
    arena1, a_bounds = build_arenas.gen_base_arena(
            length=sz, width=sz, ww=0.5, arc_steps=17)

    simctrl = sim.Control()
    
    # Spawn the Bee and the Casu
    #simctrl.spawn('Casu','casu-001',(0,0,0))
    simctrl.spawn('Bee','Bee-001',(2,0,pi/2))

    # spawn the walls
    enki_ctrl.spawn_poly_group( simctrl, arena1, (0,0,0), label_stub='arena',
            color=(0.5,0.5,0.5)    , verb=1)


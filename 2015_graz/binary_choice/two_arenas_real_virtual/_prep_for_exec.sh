#!/bin/sh


echo "[I] ASSUMING ASSISI PLAYGROUND IS RUNNING!"
echo "[I] ASSUMING DEPLOYMENT IS DONE"

# 1. run the simtool spawn
cd deployment
sim.py  real_and_virtual_two_arena_in3x3.arena
cd ..
# 2. spawn casus
python spawn_walls.py



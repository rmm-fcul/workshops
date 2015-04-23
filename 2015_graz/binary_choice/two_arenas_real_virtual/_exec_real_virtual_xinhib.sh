#!/bin/sh

# 1. start assisi_playground
# 2. 
#sim.py real_and_virtual_two_arena_in3x3.arena
#python spawn_walls.py
# 3. start the CASU programs (this should be a FG process)
#cd deployment
#assisirun.py real_and_virtual_two_arena_in3x3.arena

# 4. wait for calibration to complete

# 3. put in bees (real)
# 4. spawn bees (virtual), and start bee controllers
#python spawn_bees.py

#sleep(2)

bee_local_conf=bee-virt.conf
my_spec=../deployment/spawn_bee_locations.DATE
logpath=results/trial1
mkdir -p ${logpath}

# how to run bees? ...
python launch_bee_behaviours.py --exec-script addrs_bee_wander.py \
    --obj-listing ${my_spec} --local-conf ${bee_local_conf} \
    --logpath ${logpath}"



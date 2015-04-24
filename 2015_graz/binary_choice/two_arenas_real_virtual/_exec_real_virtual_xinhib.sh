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
python spawn_bees.py -n 15

#sleep(2)

bee_local_conf=bee-virt.conf
my_spec=../deployment/spawn_bee_locations.DATE
logpath=results/real_with_bees2
mkdir -p ${logpath}

logpath="../"${logpath}

# how to run bees? ...
cd bee_behav
cmd="python launch_bee_behaviours.py --exec-script addrs_bee_wander.py \
    --obj-listing ${my_spec} --local-conf ${bee_local_conf} \
    --logpath ${logpath}"
echo ${cmd}



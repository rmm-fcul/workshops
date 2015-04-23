#!/bin/sh

cd deployment
deploy.py oncasu_and_virtual_two_arena_xinhib_cross_between.assisi
cd ../
for f in casu_utils.py loggers.py parsing.py real-virtual-cross.conf xinhib_heaters.py; do
    scp ${f} assisi@casu-001:deploy/real_arena/casu-001
    scp ${f} assisi@casu-004:deploy/real_arena/casu-004

    scp ${f} assisi@192.168.12.79:deploy/sim-virtual_arena/casu-sim-003
    scp ${f} assisi@192.168.12.79:deploy/sim-virtual_arena/casu-sim-006
done
cd -



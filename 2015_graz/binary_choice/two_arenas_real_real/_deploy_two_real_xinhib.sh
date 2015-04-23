#!/bin/sh

cd deployment
deploy.py oncasu_two_arena_xinhib_cross_between.assisi
cd /home/rmm/repos/gh/rmm-assisi-workshops/2015_graz/binary_choice/two_arenas_real_real
for f in casu_utils.py loggers.py parsing.py two-real-with-cross.conf xinhib_heaters.py; do
    scp ${f} assisi@casu-001:deploy/sym_breaking_arena/casu-001
    scp ${f} assisi@casu-003:deploy/sym_breaking_arena/casu-003
    scp ${f} assisi@casu-004:deploy/sym_breaking_arena/casu-004
    scp ${f} assisi@casu-006:deploy/sym_breaking_arena/casu-006
done
cd -



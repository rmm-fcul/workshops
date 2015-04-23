#!/bin/sh

cd deployment
deploy.py oncasu_one_arena_xinhib.assisi
cd /home/rmm/repos/gh/rmm-assisi-workshops/2015_graz/binary_choice/single_arena
for f in parsing.py loggers.py casu_utils.py with-cross.conf; do
    scp ${f} assisi@casu-002:deploy/sym_breaking_arena/casu-002
    scp ${f} assisi@casu-005:deploy/sym_breaking_arena/casu-005
done
cd -


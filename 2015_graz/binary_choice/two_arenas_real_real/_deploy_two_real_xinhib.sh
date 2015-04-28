#!/bin/sh

# a simple script to copy additional dependencies alongside the main CASU
# controller during deployment.
#
# NOTE: makes explicit assumption for the experiment project name="sym_breaking_arena"
# NOTE: this should be obselete since assisi-python issue #20 is closed.
# initially preserving script since this workflow was used at workshop.
# Notes from April 28 following worksop


# declare deps & target CASUs
deps=casu_utils.py loggers.py parsing.py two-real-with-cross.conf xinhib_heaters.py
casus=001 003 004 006

# first, run the built-in deployment (this creates relevant directories on remote side, as well as deploying the main config)
cd deployment
deploy.py oncasu_two_arena_xinhib_cross_between.assisi
cd ..

# now copy all extra dependencies
for f in ${deps}; do
    for casu in ${casus}; do
        scp ${f} assisi@casu-${casu}:deploy/sym_breaking_arena/casu-${casu}
    done
done
cd -



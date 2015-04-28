Two arenas (real-real)
======================

An experiment comprising two arenas, each of 2 CASUs and a group of bees.  The
CASUs in each arena compete to attract the bees, through a positive feedback 
coupling between the presence of bees and temperature emitted by the CASUs. 
Additionally, there is a negative feedback coupling between CASUs in the same
arena, i.e., lateral cross-inhibition (between 'enemy' CASUs).

Finally, to test whether we can coordinate activity/collective decisions made
in both arenas, we also introduce coupling between specific pairs of CASUs: in
each arena, each CASU has a collaborator ('friend') in the other arena.  They
share their local bee detection estimates, which can be thought of as giving
each CASU 12 IR sensors instead of 6.


To run this experiment, we use the deployment tools from assisi-python.
However, one extra helper script is used in deployment:



Protocol used to run experiments
--------------------------------

1. cd <workshops_repo_home>/2015_graz/binary_choice/two_arenas_real_real

2. deploy the programs
./_deploy_two_real_xinhib.sh

3. start the CASU controllers, *with lab door shut* or under whatever lighting
   conditions the experiment will run in

cd deployment
assisirun.py oncasu_two_arena_xinhib_cross_between.assisi

4. wait for all CASUs to finish IR sensor calibration (approx 10 sec; displayed
   in terminal)

5. start video recordings as appropriate

6. put bees into both arenas
   restore lab conditions as for #3



Alternative topology
--------------------

The central topology provided here uses CASUs [1,3] and [4,6] in two arenas,
and couples them in a "cross" pattern.  This means that if there is any thermal
coupling from one arena to the other, a successful coordination has to work
against it.

To change the topology to a "horizontal links" pattern (where both arenas will
choose top or both choose bottom, if successfully coordinated), the following
files should be modified:

./
  oncasu_two_arena_xinhib_cross_between.assisi
  s/two-real-with-cross.conf/two-real-with-horiz.conf/
   
deployment/
  oncasu_two_arena_xinhib_cross_between.assisi
  s/two_arena_cross_in3x3.nbg/two_arena_horizontal_in3x3.nbg/

  








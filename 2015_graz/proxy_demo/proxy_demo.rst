Proxy demo
==========

We have a progression of three versions:

1. a single bee that circles around the single CASU, thus generating regular stimulus.

2. a single bee that wanders around a small arena with one CASU, generating less specific stimulus (but obviously more realistic)

3. a 3x3 CASU array, and a configurable number of wandering bees.   


Single circling bee
-------------------

- start the simulator: assisi_playground
- spawn agents: spawn_casu_and_bee.py
- run the single bee behaviour: bee_circling.py
- run the CASU: casu_sensing.py casu.rtc
 

Single wandering bee
--------------------

- start the simulator: assisi_playground
- spawn casu
- run CASU (so that the calibration can commence before any bees present)
- spawn walls and bees: spawn_walls_and_bees.py -n 1
- run the single bee behaviour: bees_wander.py -n 1


**Extend to >1 bee, single CASU**:

minor deviation from above:
assisi_playground
- window 1:
./spawn_casus.py
./casu_sensing.py

- window 2:
./spawn_walls_and_bees.py -n <N> -r <R>
./bees_wander.py -n <N>

(the big arena is 35cm across)
(the smaller arena is 12.6cm across)

Multiple CASUs
--------------

We follow a similar procedure, but use the deployment tool to manage the CASU side of things.

assisi_playground

- window 1:
  cd deployment
  sim.py simple_3x3-sim.arena
  deploy.py sim_3x3_local.assisi
  assisirun.py sim_3x3_local.assisi

- window 2:
  once calibration is complete, we can do the bee spawn
  ./spawn_walls_and_bees.py -n 10 -r 35
  ./bees_wander.py -n 10

  
**single CASU, with deployment tool**
  sim.py simple_just001-sim.arena
  deploy.py sim_just_001.assisi
  assisirun.py sim_just_001.assisi


**physical CASUs**

- window 1:
  cd deployment

deploy.py casu_3x3.assisi
assisirun.py casu_3x3.assisi

that's it - the "equivalent" of spawn_bees is to put the bees into arena at this point.









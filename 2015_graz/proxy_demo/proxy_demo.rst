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
- run the CASU: casu_sensing.py
 

Single wandering bee
--------------------

- start the simulator: assisi_playground
- spawn casu
- run CASU (so that the calibration can commence before any bees present)
- spawn walls and bees: spawn_walls_and_bees.py -n 1
- run the single bee behaviour: bee_wandering.py 


**Extend to >1 bee, single CASU**:

minor deviation from above:
assisi_playground
- window 1:
./spawn_casus.py
./casu_sensing.py

- window 2:
./spawn_walls_and_bees.py -n <N>
./bees_wander.py -n <N>



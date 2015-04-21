.. _deployment_examples:

Simple deployment scenario examples
-----------------------------------

All the files necessary for running the examples below can be found in
the ``examples/deployment/simple`` folder. Both examples assume a
3x3 CASU array. The same controller, located in the ``controllers``
subfolder, is deployed to all CASUs. It just turns its diagnostic led
on and off and sends a message to its neighbors.

Local deployment with simulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To run this example as-is, without any modifications, you will need to
set up an user account for the user `assisi` on your machine, and set
up :ref:`ssh_nopass` from you regular user to the `assisi` user.

First start the assisi-playground simulator with
default options and spawn the CASUs:
::

   sim.py simple_3x3-sim.arena

Then, deploy the controllers to the home folder of
the `assisi` user:
::

   deploy.py sim_3x3_local.assisi

Run the deployed controllers:
::

   assisirun.py sim_3x3_local.assisi

and see the simulated CASUs blink their LEDs. Type `Ctrl-C` in the
same terminal to stop the controllers.

After stopping the controllers, your terminal command line might
become corrupted (i.e. it looses the carriage-return and commands you
type are not displayed). To restore the terminal, just type:
::

   <Ctrl-J>reset<Ctrl-J>

For more info on resetting the terminal, check out `this link <http://manpages.ubuntu.com/manpages/utopic/man1/tset.1.html>`_.

To retreive the data logged by the casu controllers, run:
::

   collect_data.py sim_3x3_local.assisi --clean

The logfiles will be stored in a new subfolder called
`data_sim_3x3_local`. The `--clean` option removes the original log
files after copying them.

The ``sim_3x3_local.assisi`` file is a yaml-formated file that lists the files describing
your project:

.. literalinclude:: ../../examples/deployment/simple/sim_3x3_local.assisi

The ``simple_3x3-sim.arena`` file is a yaml-formatted file that
describes the arena layout (physical CASU locations) and their TCI/IP URIs:

.. literalinclude:: ../../examples/deployment/simple/simple_3x3-sim.arena

The ``simple_3x3-sim.nbg`` file is a Graphviz dot-formatted file that
describes the communication network topology between the CASUs:

.. literalinclude:: ../../examples/deployment/simple/simple_3x3-sim.nbg

You can visualize the neighborhood graph with the command:
::

   dot -Tpdf -O simple_3x3.nbg

which will create a ``.pdf`` file with the neighborhood graph.

The ``local.dep`` file is a yaml-formatted file that specifies the
controller code to deploy to individual casus and connection details
for the deployment target:

.. literalinclude:: ../../examples/deployment/simple/local.dep

Deployment to CASUs
~~~~~~~~~~~~~~~~~~~

Make sure that you can establish an ssh connection from the
development host to all of the CASUs, without being prompted for a
password. Then, simply deploy:
::

   deploy.py casu_3x3.assisi

and run:
::

   assisirun.py casu_3x3.assisi

and observe the CASUs blinking their LEDs. Type `Ctrl-C` to stop the controllers.

After stopping the controllers, your terminal command line might
become corrupted (i.e. it looses the carriage-return and commands you
type are not displayed). To restore the terminal, just type:
::

   <Ctrl-J>reset<Ctrl-J>

For more info on resetting the terminal, check out `this link <http://manpages.ubuntu.com/manpages/utopic/man1/tset.1.html>`_.

To retreive the data logged by the casus, run:
::

   collect_data.py sim_3x3_local.assisi

The logfiles will be stored in a new subfolder called
`data_sim_3x3_local`. The `--clean` option removes the original
logfiles after copying them.

The ``sim_3x3_local.assisi`` file is a yaml-formated file that lists the files describing
your project:

.. literalinclude:: ../../examples/deployment/simple/casu_3x3.assisi

The ``simple_3x3-sim.arena`` file is a yaml-formatted file that
describes the arena layout (physical CASU locations) and their TCI/IP URIs:

.. literalinclude:: ../../examples/deployment/simple/simple_3x3.arena

The ``simple_3x3-sim.nbg`` file is a Graphviz dot-formatted file that
describes the communication network topology between the CASUs:

.. literalinclude:: ../../examples/deployment/simple/simple_3x3.nbg

You can visualize the neighborhood graph with the command:
::

   dot -Tpdf -O simple_3x3.nbg

which will create a ``.pdf`` file with the neighborhood graph.

The ``local.dep`` file is a yaml-formatted file that specifies the
controller code to deploy to individual casus and connection details
for the deployment target:

.. literalinclude:: ../../examples/deployment/simple/casu.dep



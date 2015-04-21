
from fabric.api import cd, run, settings, parallel

@parallel
def sim_01_casu_003():
    with settings(host_string='localhost', user='assisi'):
        with cd('deploy/sim-01/casu-003'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send.py casu-003.rtc')
                                  
@parallel
def sim_01_casu_002():
    with settings(host_string='localhost', user='assisi'):
        with cd('deploy/sim-01/casu-002'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send.py casu-002.rtc')
                                  
@parallel
def sim_01_casu_001():
    with settings(host_string='localhost', user='assisi'):
        with cd('deploy/sim-01/casu-001'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send_seed.py casu-001.rtc')
                                  
@parallel
def sim_01_casu_007():
    with settings(host_string='localhost', user='assisi'):
        with cd('deploy/sim-01/casu-007'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send.py casu-007.rtc')
                                  
@parallel
def sim_01_casu_006():
    with settings(host_string='localhost', user='assisi'):
        with cd('deploy/sim-01/casu-006'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send.py casu-006.rtc')
                                  
@parallel
def sim_01_casu_005():
    with settings(host_string='localhost', user='assisi'):
        with cd('deploy/sim-01/casu-005'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send.py casu-005.rtc')
                                  
@parallel
def sim_01_casu_004():
    with settings(host_string='localhost', user='assisi'):
        with cd('deploy/sim-01/casu-004'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send.py casu-004.rtc')
                                  
@parallel
def sim_01_casu_009():
    with settings(host_string='localhost', user='assisi'):
        with cd('deploy/sim-01/casu-009'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send.py casu-009.rtc')
                                  
@parallel
def sim_01_casu_008():
    with settings(host_string='localhost', user='assisi'):
        with cd('deploy/sim-01/casu-008'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send.py casu-008.rtc')
                                  
def all():
    sim_01_casu_003()
    sim_01_casu_002()
    sim_01_casu_001()
    sim_01_casu_007()
    sim_01_casu_006()
    sim_01_casu_005()
    sim_01_casu_004()
    sim_01_casu_009()
    sim_01_casu_008()

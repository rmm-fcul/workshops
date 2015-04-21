
from fabric.api import cd, run, settings, parallel

@parallel
def beearena_casu_003():
    with settings(host_string='casu-003', user='assisi'):
        with cd('deploy/beearena/casu-003'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send.py casu-003.rtc')
                                  
@parallel
def beearena_casu_002():
    with settings(host_string='casu-002', user='assisi'):
        with cd('deploy/beearena/casu-002'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send.py casu-002.rtc')
                                  
@parallel
def beearena_casu_001():
    with settings(host_string='casu-001', user='assisi'):
        with cd('deploy/beearena/casu-001'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send_seed.py casu-001.rtc')
                                  
@parallel
def beearena_casu_007():
    with settings(host_string='casu-007', user='assisi'):
        with cd('deploy/beearena/casu-007'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send.py casu-007.rtc')
                                  
@parallel
def beearena_casu_006():
    with settings(host_string='casu-006', user='assisi'):
        with cd('deploy/beearena/casu-006'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send.py casu-006.rtc')
                                  
@parallel
def beearena_casu_005():
    with settings(host_string='casu-005', user='assisi'):
        with cd('deploy/beearena/casu-005'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send.py casu-005.rtc')
                                  
@parallel
def beearena_casu_004():
    with settings(host_string='casu-004', user='assisi'):
        with cd('deploy/beearena/casu-004'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send.py casu-004.rtc')
                                  
@parallel
def beearena_casu_009():
    with settings(host_string='casu-009', user='assisi'):
        with cd('deploy/beearena/casu-009'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send.py casu-009.rtc')
                                  
@parallel
def beearena_casu_008():
    with settings(host_string='casu-008', user='assisi'):
        with cd('deploy/beearena/casu-008'):
                run('export PYTHONPATH=/home/assisi/python:$PYTHONPATH; ./blink_and_send.py casu-008.rtc')
                                  
def all():
    beearena_casu_003()
    beearena_casu_002()
    beearena_casu_001()
    beearena_casu_007()
    beearena_casu_006()
    beearena_casu_005()
    beearena_casu_004()
    beearena_casu_009()
    beearena_casu_008()

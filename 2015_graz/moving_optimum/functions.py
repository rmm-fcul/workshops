
'''
Functions for interactive use in moving optimum experiment/illustration

This includes two different experiments:
1. an abrupt change of locations of LO & GO, from TL/BR to BL/TR
2. a gradual change of locations, from TL/BR->ML/MR->TL/BR
(where LO/GO=local/global optimum; TR/BL=top right/bottom left etc)

Both start with 
C = connect_all_casus()
phase1(C);
Then they split:
1 ->
phase2(C, base_temp=29); 

2 ->
phase_inter(C, base_temp=29); 
phase_third(C, base_temp=29); 


See below for a more detailed flow of each of the two experiments as we ran them


Example usage (abrupt change):
	# load the functions	
	%run functions.py
	# obtain handles to all 9 casus 
	C = connect_all_casus()
	# start the first phase, which, by default sets the optima to 32/36.
	# (we do not put the bees in until the temps have stabilised)
	phase1(C); start_time = time.time()
	# monitor the temperatures from time to time
	easy_temps(C, start_time)
	# once they have stabilised, put in the bees
	bees_in_time = time.time()
	# while we wait for aggregation, we can monitor temperatures (use 2nd ref time)
	easy_temps(C, bees_in_time)
	# once deemed to have aggregation at the first G.O., we move to 2nd phase
	# choose the ambient temperature to actively cool, based on the thermal 
	# camera reading.
	phase2(C, base_temp=29); time_phase2 = time.time()
	# can use any of the refernce times
	easy_temps(C, start_time)
	easy_temps(C, bees_in_time)
	easy_temps(C, time_phase2)
	# once we've done, record the stop_time
    stop_time = time.time()
    # all casus to standby
    all_standby(C)
    all_stop(C)
    # when the casu handles are closed, the logfiles are saved, so quit the 
    # ipython session.
    quit
    

'''

'''
example usage (gradual change):
	# load the functions	
	%run functions.py
	# obtain handles to all 9 casus 
	C = connect_all_casus()
	# start the first phase, which, by default sets the optima to 32/36.
	# (we do not put the bees in until the temps have stabilised)
	phase1(C, global_temp=35.5, local_temp=32); start_time = time.time()
	# monitor the temperatures from time to time
	easy_temps(C, start_time)
	# once they have stabilised, put in the bees
	bees_in_time = time.time()
	# while we wait for aggregation, we can monitor temperatures (use 2nd ref time)
	easy_temps(C, bees_in_time)
	# once deemed to have aggregation at the first G.O., we move to intermediate phase
	# choose the ambient temperature to actively cool, based on the thermal 
	# camera reading.
	phase_inter(C, base_temp=29); time_phase_inter = time.time()
	
	# can use any of the refernce times
	easy_temps(C, start_time)
	easy_temps(C, bees_in_time)
	easy_temps(C, time_phase_inter)
	
	# once we have seen that the bees are being guided (softer criterion??), we
	# move to the final stage
	phase_third(C, base_temp=29); time_phase_final = time.time()
	easy_temps(C, time_phase_final)
	# possibly adjust the temp on casu-009 because thermometer low reading?
	C[8].set_temp(34)
	
	# once we've done, record the stop_time
    stop_time = time.time()
    # all casus to standby
    all_standby(C)
    all_stop(C)
    # when the casu handles are closed, the logfiles are saved, so quit the 
    # ipython session.
    quit
'''


from assisipy import casu
import time
from time import gmtime, strftime
from pytz import timezone


def show_all_temps(c):
	'''
	display all four temperature sensor values for one casu.
	IF you have the array of casu handles in C, type 
	   show_all_temps(C[8]) for the casu-009 temperatures
	
	'''
	for sensor in [casu.TEMP_F, casu.TEMP_R, casu.TEMP_B, casu.TEMP_L]: 
		print c.get_temp(sensor)


def mean(l):
	''' arithmetic mean of list of numbers'''
	return float(sum(l))/len(l) if len(l) > 0 else float('nan')

def connect_all_casus(top=9, rtc_path='physical'):
	'''
	returns a list of handles to the list of casus 1..top.
	assumes that RTC files exist in the directory rtc_path/casu-xxx/casu-xxx.rtc
	these files are created by the deployment part of assisipy (see example 
	"deployment").
	'''
	C = []
	for n in xrange(1, 1+top):
		rtc = '{0}/casu-{1:03d}/casu-{1:03d}.rtc'.format(rtc_path, n)
		print "using casu {}".format(rtc)
		C.append(casu.Casu(rtc_file_name=rtc, log=True))
	
	return C

def get_all_temperatures(C): 
	'''
	given a list of CASU handles in C, read all the external temperatures for
	each one, compute the mean, and return that as a list
	'''
	mean_temps = []
        for mycasu in C:
            temps = []
            for sensor in [casu.TEMP_F, casu.TEMP_R, casu.TEMP_B, casu.TEMP_L]:
                t = mycasu.get_temp(sensor)
                if t < 100.0 and t > 18.0:
                    # some of the CASUs don't have all 4 sensors; they seem to 
                    # report out of bounds numbers so we just ignore anythig
                    # taht is infeasible
                    temps.append(t)

            mean_temps.append(mean(temps))

	return mean_temps
		


def show_temperatures_3x3_countup(temps, fmt = "5.2f"):
	'''
	a func to show a grid of temperatures, assuming a 3x3 topology:
	123
	456
	789
	'''
	
	for x in xrange(3):
		s = "\t"
		for y in xrange(3):
			i = y + x *3
			s+= "{:03d}: {:{fmt}}oC\t".format(i+1, temps[i], fmt=fmt)
		print s

def show_temperatures_3x3(temps, fmt = "5.2f"):
	'''
	a func to show a grid of temperatures, oriented as per the cameras,
	assuming this 3x3 topology:	
	987
	654
	321
	'''
	
	for x in xrange(2, -1, -1):
		s = "\t"
		for y in xrange(2, -1, -1):
			i = y + x *3
			s+= "{:03d}: {:{fmt}}oC\t".format(i+1, temps[i], fmt=fmt)
		print s
	 	 
			
def easy_temps(C, start_time):
	'''
	display the mean temperature on all casus, and indicate current time and 
	time elapsed since the parameter `start_time`
	'''
	T = get_all_temperatures(C); 
	show_temperatures_3x3(T);
	elap = time.time() - start_time
	_m = int(elap) / 60
	_s = int(elap) - (60*_m)
	elap_str =  "{}m{}s".format(_m, _s)
	print "At time {} (time elapsed: {})".format(
		strftime("%H:%M:%S %Z", gmtime()), elap_str)


def all_to_standby(C):
	for mycasu in C:
		mycasu.temp_standby()


def all_stop(C):
	for mycasu in C:
		mycasu.stop()

    
def phase1(C, global_temp=36, local_temp=32):
    C[2].set_temp(global_temp)
    #C[2].set_diagnostic_led_rgb(r=1)
    
    C[6].set_temp(local_temp)
    #C[6].set_diagnostic_led_rgb(g=1)
    
    print("set casu-3 to global temp{}".format(global_temp))
    print("set casu-7 to local temp{}".format(local_temp))
    
def phase_inter(C, global_temp=36, local_temp=32, base_temp=28):

    print("set casu-3 and -7 to base temp: {}".format(base_temp))
    C[2].set_temp(base_temp)
    C[6].set_temp(base_temp)
    
    print("set casu-6 to global temp:      {}".format(global_temp))
    C[5].set_temp(global_temp)
    
    print("set casu-4 to local temp:       {}".format(local_temp))
    C[3].set_temp(local_temp)
 
def phase_third(C, global_temp=36, local_temp=32, base_temp=28):
    # first we turn all to standby (for temperature), to be sure we are only
    # setting exactly 4 values
    all_to_standby(C)
    # and now set the final temps
    print("set casu-4 and -6 to base temp: {}".format(base_temp))
    C[3].set_temp(base_temp)
    C[5].set_temp(base_temp)

    print("set casu-9 to global temp:      {}".format(global_temp))
    C[8].set_temp(global_temp)
    
    print("set casu-1 to local temp:       {}".format(local_temp))
    C[0].set_temp(local_temp)
      
      
def phase2(C, global_temp=36, local_temp=32, base_temp=28):
    C[8].set_temp(global_temp)
    #C[8].set_diagnostic_led_rgb(r=1)
    
    C[0].set_temp(local_temp)
    #C[0].set_diagnostic_led_rgb(g=1)
    
    C[2].set_temp(base_temp)
    #C[2].set_diagnostic_led_rgb(b=1)
    
    C[6].set_temp(base_temp)
    #C[6].set_diagnostic_led_rgb(b=1)
    
    print("set casu-9 to global temp{}".format(global_temp))
    print("set casu-1 to local temp{}".format(local_temp))
    print("set casu-3 and -6 to base temp{}".format(base_temp))


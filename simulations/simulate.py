from __future__ import division
#######################################################
# ** DO NOT MODIFY THIS
# ** USING MODELS OUTSIDE OF DJANGO
from django.core.management import setup_environ
import settings
try:
	setup_environ(settings)
except ImportError:
	raise Exception("""ERROR: You must set the environment variable 
		DJANGO_SETTINGS_MODULE to 'corporate_epidemiology.settings'
		e.g.:>>>export DJANGO_SETTINGS_MODULE=corporate_epidemiology.settings""")
#########################################################
#from simulations.calculations import program_si
from simulations import calculations
from simulations.parameters import get_parameters, generate_initial_infected
from simulations.models import *

import uuid, time
from itertools import *
from optparse import OptionParser

#######################################################
# ** MUST SPECIFY PARAMETER SETS HERE
from numpy import arange
#	BETA: TRANSMISSION RATE
beta=[1] #beta = arange(1,1.5,0.1)
#	GAMMA rate of recovery (in seconds?)
gamma=[1/10000]  # gamma = arange(0.4, 0.6, 0.1)
#	ALPHA: sendhome parameter: NOTE: 0 < alpha < 1 : the fraction of total infection period to wait before going home
alpha=[.7]
#	TIMESTEP (NOT USED WITH SI MODEL)
timestep = [0.1]
#	MAX_TIME (NOT USED WITH SI MODEL)
max_time = [100]
#	T_MIN_FILTER
t_min_filter = [0]
#	T_MAX_FILTER
t_max_filter = [4000]
#######################################################


############################
# ** MAIN FUNCTION
#		READS COMMAND LINE OPTIONS
#		CALLS 
def main():
	# ** OPTIONS
	usage = "\n\tpython simulations/simulate.py --simulation_name='program_sir_sendhome' --infection='standard_infection' --recovery='standard_recovery' --sendhome='standard_sendhome' --initial_infected='expansive_max' --iiN=2 --dryrun=True --test_number=3"

	parser = OptionParser(usage)
	# INFECTION KERNEL: DEFAULT = standard_infection (see infections.py)
	parser.add_option("--infection", 
					action="store", dest="infection_function", default='standard_infection',
					help="Specify which infection function to use.  See infections.py\n")
	# RECOVERY KERNEL: DEFAULT = standard_recovery (see recovery.py). NOT USED WITH SI
	parser.add_option("--recovery", 
					action="store", dest="recovery_function", default='standard_recovery',
					help="Specify which recovery function to use.  See recovery.py\n")
	# SENDHOME KERNEL: DEFAULT = standard_sendhome (see sendhome.py). NOT USED WITH SI
	parser.add_option("--sendhome", 
					action="store", dest="sendhome_function", default='standard_sendhome',
					help="Specify which sendhome function to use.  See sendhome.py\n")
	# SPECIFY HOW TO GENERATE THE INITIAL INFECTED SETS
	parser.add_option("--initial_infected", 
					action="store", dest="initial_infected", default='each',
					help="Specify how to generate the initial infections.  See parameters.py\n")
	# SPECIFY N FOR INITIAL INFECTED.  ONLY USED WITH --initial_infected = ("combo", "expansive_max")
	parser.add_option("--iiN", 
					action="store", dest="iiN", default='3',
					help="Specify N for some initial infections.  See parameters.py\n")
	# MULTIPLICITY
	parser.add_option("--M", 
					action="store", dest="multiplicity", default=1,
					help="Specify multiplicity of parameter sets.  See parameters.py\n")
	# WHICH FUNCTION TO USE FOR SIMULATION: allows switching between SI, SIR, etc
	parser.add_option("--simulation_name", 
					action="store", dest="simulation_name", default='program_sir_sendhome',
					help="Specify which simulation to use.  See calculations.py\n")

	# TEST RUN
	parser.add_option("--test_number",
					action="store", dest="test_number", default=0,
					help="Pass in an integer that will only run N simulations...an easy way to start small\n")

	
	# DRY RUN
	parser.add_option("--dryrun",
					action="store", dest="dryrun", default=False,
					help="SHOW WHICH PARAMETERS WILL BE USED.  Calculate estimated time\n")

	##########################################
	# ** PARSE OPTIONS
	(options, args) = parser.parse_args()

	##############################################
	# ** STORE OPTIONS
	#print options
	infection_function = options.infection_function
	recovery_function  = options.recovery_function
	sendhome_function  = options.sendhome_function
	initial_infected   = options.initial_infected # each, combo, expansive, expansive_max
	N                  = int(options.iiN) # INITIAL INFECTED N
	M                  = int(options.multiplicity) # MULTIPLICITY
	dryrun             = options.dryrun
	simulation_name    = options.simulation_name
	test_number        = int(options.test_number)

	###############################################
	###############################################
	# ** GENERATE SETS OF INITIAL INFECTIONS
	#		MUST USE: 0 < N < (# of individuals)
	###############################################
	Y0=generate_initial_infected(option=initial_infected, N=N, dryrun=dryrun, test_number=test_number)
	# ** GENERATE PARAMETER SETS: THIS CAN BE EDITED
	#parameter_set = list(product(beta, gamma, alpha, Y0, timestep, max_time, t_min_filter, t_max_filter))
	
	###################################################################################
	# ** NEEDS UPDATING TO HANDLE SI & SIR gracefully: currently hard-coded for each
	if simulation_name == 'program_si':
		parameter_set = list(product(beta, Y0, t_min_filter, t_max_filter)) # USED FOR SI CALCULATIONS
	elif simulation_name=='program_sir_sendhome':
		parameter_set = list(product(beta, gamma, alpha, Y0, t_min_filter, t_max_filter)) # USED FOR SIR CALCULATIONS
	###################################################################################
	
	
	# ** INCORPORATE MULTIPLICITY TO RUN SAME PARAMETER SETS M-TIMES
	full_parameter_set = M*parameter_set
	
	number_of_simulations = len(full_parameter_set)
	counter = 0
	
	# PRINT USEFUL INFO
	if dryrun:
		print '\n\tDRY RUN: infection, \t\trecovery, \t\tsendhome, beta,\t\tgamma, \t\talpha, \t\t\tY0, tmin, tmax\n'

	for set_of_parameters in full_parameter_set:
		counter+=1
		print 'On %s of %s' % (counter, number_of_simulations)
		###########################################
		# ** RUN SINGLE SIMULATION with parameters
		#		This function must:
		#			STORE SIMRUN
		#			STORE INITIAL INFECTED
		#			STORE TIME SERIES: S, I, R (optional)
		#			STORE NETWORK DATA  
		# LOAD SIMULATION FUNCTION TO USE
		try:
			simulation = getattr(calculations,simulation_name) # i.e. program_sir
		except AttributeError:
			raise Exception('\n\nERROR:\t--simulation_name=%s does not correspond to known function. \n\t\tCheck simulations/calculations.py for valid function names.' % simulation_name)
		
		# RUN SINGLE SIMULATION
		simulate = simulation(infection_function, recovery_function, sendhome_function, set_of_parameters, dryrun=dryrun)


if __name__ == "__main__":
	main()




















#def simulate(infection_function=None, recovery_function=None):
#	"""
#	Main program to control the simulation.
#	
#	It will run all simulations based on all the parameter sets you specify, along with the multiplicity of each one
#		(i.e. run 10 simulations using the following parameter values (alpha=1, beta=1.1,...)
#	"""
#	if infection_function is None:
#		infection_function = 'standard'
#	if recovery_function is None:
#		recovery_function = 'standard'
#		
#	################################
#	# ** Get all parameter sets
#	parameters = get_parameters('each')
#	#parameters = get_parameters('combo',3)
#	#parameters = get_parameters('expansive')
#	#parameters = get_parameters('expansive_max',3)
#	
#	####################
#	# ** Shows you the parameters you are about to run your simulations with 
#	if dryrun:
#		print "This will run %s simulations with the following parameters\n"
#		time.sleep(1)
#		print parameters
#		return None
#	
#	# Loop through each set:
#	for parameter_set in parameters:
#		# GET PARAMETERS
#		beta, gamma, alpha, Y0, timestep, max_time, t_min_filter, t_max_filter = parameter_set
#		
#		# Generate unique id for run
#		sim_uuid = str(uuid.uuid4())[0:30]
#
#		# RUN SIMULATION
##		try:
#		# GENERATE TIME SERIES using the simulation kernal defined in simulations/calculations.py
#		try:
#			print "\tExecuting:\n\t\tbeta:%s\n\t\tY0:%s\n\t\t%s\n\t\t%s" % (beta, Y0, t_min_filter, t_max_filter)
#			S, I, T = program_si(beta, gamma, alpha, Y0, timestep, max_time, t_min_filter, t_max_filter, infection_function)
#		except:
#			continue
#		
#		# DERIVATIVE CALCULATIONS ON time series data  
#		
#		
#		# CREATE DICTIONARY TO LOAD VARIABLE SIMRUN PARAMETERS
#		simulation_dict = {
#						'beta':beta,
#						'gamma':gamma,
#						't_min_filter':t_min_filter,
#						't_max_filter':t_max_filter,
#						}
#
#		# STORE PARAMETERS
#		sim_run = SimRun.objects.create(
#									sim_uuid=sim_uuid,
#									infection_function=infection_function,
#									 **simulation_dict)
#		
#		# TURN SINGLE INDIVIDUAL INTO A LIST
#		if isinstance(Y0,int):
#			Y0=(Y0,)
#		# STORE INITIAL INFECTED
#		for ind_uuid in Y0:
#			individual = Individual.objects.get(ind_uuid=ind_uuid)
#			ii = InitialInfected.objects.create(sim_run=sim_run, individual_infected=individual)
#		
#		# STORE S, I, T
#		for s, i, t in zip(S,I,T):
#			SimTimeSeries.objects.create(sim_run=sim_run,susceptible=s,infected=i,t=t)
##		except:
##			continue



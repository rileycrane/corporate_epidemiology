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
from simulations.calculations import program_sir
from simulations.parameters import get_parameters
from simulations.models import *
import uuid


def simulate(infection_function=None):
	"""
	Main program to control the simulation.
	
	It will run all simulations based on all the parameter sets you specify, along with the multiplicity of each one
		(i.e. run 10 simulations using the following parameter values (alpha=1, beta=1.1,...)
	"""
	if infection_function is None:
		infection_function = 'standard'

	# Get all parameter sets
	parameters = get_parameters()
	
	# Loop through each set:
	for parameter_set in parameters:
		# GET PARAMETERS
		beta, gamma, alpha, Y0, timestep, max_time, t_min_filter, t_max_filter = parameter_set
		
		# Generate unique id for run
		sim_uuid = str(uuid.uuid4())[0:30]

		# RUN SIMULATION
#		try:
		# GENERATE TIME SERIES using the simulation kernal defined in simulations/calculations.py
		S, I, T = program_sir(beta, gamma, alpha, Y0, timestep, max_time, t_min_filter, t_max_filter, infection_function)
		
		# DERIVATIVE CALCULATIONS ON time series data  
		
		# STORE PARAMETERS
		sim_run = SimRun.objects.create(sim_uuid=sim_uuid,calculation_name='program_sir',
									beta=beta, gamma=gamma, alpha=alpha,
									timestep=timestep,max_time=max_time,
									t_min_filter=t_min_filter, t_max_filter=t_max_filter)
		
		# TURN SINGLE INDIVIDUAL INTO A LIST
		if isinstance(YO,int):
			Y0=[Y0]
		# STORE INITIAL INFECTED
		for ind_uuid in Y0:
			individual = Individual.objects.get(ind_uuid=ind_uuid)
			ii = InitialInfected.objects.create(sim_run=sim_run, individual_infected=individual)
		
		# STORE S, I, T
		for s, i, t in zip(S,I,T):
			SimTimeSeries.objects.create(sim_run=sim_run,susceptible=s,infected=i,t=t)
#		except:
#			continue
	

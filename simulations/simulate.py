from simulations.calculations import program_sir
from simulations.parameters import get_parameters
from simulations.models import *
import uuid


def simulate(calculation):
	"""
	Main program to control the simulation.
	
	It will run all simulations based on all the parameter sets you specify, along with the multiplicity of each one
		(i.e. run 10 simulations using the following parameter values (alpha=1, beta=1.1,...)
	"""
	
	# Get all parameter sets
	parameters = get_parameters()
	
	# Loop through each set:
	for parameter_set in parameters:
		# GET PARAMETERS
		beta, gamma, alpha, Y0, timestep, max_time, t_min_filter, t_max_filter = parameter_set
		
		# Generate unique id for run
		sim_uuid = str(uuid.uuid4())[0:30]

		# RUN SIMULATION
		try:
			# GENERATE TIME SERIES
			S, I, T = program_sir(beta, gamma, alpha, Y0, timestep, max_time, t_min_filter, t_max_filter)
			# STORE PARAMETERS
			sim_run = SimRun.objects.create(uuid=sim_uuid,calculation_name='program_sir',
										beta=beta, gamma=gamma, alpha=alpha, Y0=Y0,
										timestep=timestep,max_time=max_time,
										t_min_filter=t_min_filter, t_max_filter=t_max_filter)
			# STORE S, I, T
			for s, i, t in zip(S,I,T):
				SimTimeSeries.objects.create(sim_run=sim_run,s,i,t)
		except:
			continue
	# Initialize Simulation Result
	result = SimRun(uuid=uuid)
	

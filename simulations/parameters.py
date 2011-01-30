from itertools import *
from simulations.models import Individual

# SPECIFY THE SETS OF PARAMETERS FOR THE SIMULATION
#  ** OVERVIEW
#  Each simulation requires (i, t_min, t_max, alpha, beta)
#	Y0    = [id1, id2, ...] where each id = individual to be infected
#		  = [id1]
#		  = [id1, id3, id4]
#		  = 10 # Randomly select 10 individuals 
		
#	t_min = Minimum valid contact time
#	t_max = Maximum valid contact time
#	beta  = probability of disease transmission
#	gamma = recovery rate
#   function [t,X,Y] = Program_SIR(N, Size, beta, gamma, alpha , Y0, timestep, MaxTime)

# SPECIFY THE INITIAL PARAMETERS
def set_initial_parameters(dry_run=None):
	"""
	SPECIFY PARAMETER SETS
	"""
	from numpy import arange
	#beta = arange(1,1.5,0.1)
	# gamma = arange(0.4, 0.6, 0.1)
	if dry_run is None:
		dry_run = False
		
	if not dry_run:
		beta=[1,2]
		gamma=[5,6]
		alpha = [None]
		Y0=[4]
		timestep = [1]
		max_time = [100]
		t_min_filter = [1,2,3]
		t_max_filter = [6,7]
		multiplicity = 2 # i.e. number of times to run each simulation with same parameters
	else:
		beta=[1]
		gamma=[2]
		alpha = [None]
		Y0=[Individual.objects.all().order_by('?')[0].ind_uuid] # Get one random individual
		timestep = [1]
		max_time = [100]
		t_min_filter = [1]
		t_max_filter = [7]
		multiplicity = 1 # i.e. number of times to run each simulation with same parameters
		
	return beta, gamma, alpha, Y0, timestep, max_time, t_min_filter, t_max_filter, multiplicity

# COMBINES PARAMETER SETS
def get_parameters(dry_run=None):
	beta, gamma, alpha, Y0, timestep, max_time, t_min_filter, t_max_filter, multiplicity = set_initial_parameters(dry_run)
	parameter_set = list(product(beta, gamma, alpha, Y0, timestep, max_time, t_min_filter, t_max_filter))
	full_parameter_set = multiplicity*parameter_set
	return full_parameter_set

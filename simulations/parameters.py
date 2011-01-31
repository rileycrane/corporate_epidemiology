from itertools import *
from simulations.models import Individual

# SPECIFY THE SETS OF PARAMETERS FOR THE SIMULATION
#  ** OVERVIEW
#  Each simulation requires (i, t_min, t_max, alpha, beta)
#	Y0    = [id1, id2, ...] where each id = individual to be infected
#		  = [id1]
#		  = [id1, id3, id4]
#		  = 10 # Randomly select 10 individuals 
		
#	t_min_filter = sets the MINIMUM valid contact time.  if the duration of contact was less
#					than this, we will exclude it from the simulation
#	t_max_filter = sets the MAXIMUM valid contact time.  if the duration of contact was greater
#					than this, we will exclude it from the simulation
#	beta  = probability of disease transmission
#	gamma = recovery rate
#   function [t,X,Y] = Program_SIR(N, Size, beta, gamma, alpha , Y0, timestep, MaxTime)
def powerset(iterable):
	"""
	powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
	usage: list(powerset([1,2,3]))
	"""
	s = list(iterable)
	return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def generate_initial_infected(option=None, N=None):
	"""
	Several options
		each: 
			Generate a list that will make each person the seed once
		combo=N: 
			Generate a list that makes each N-tuple infected
			N=3: ((1,2,3),(2,3,4),(3,4,5),(1,3,4)....)
		expansive:
			Generate every possible combination ((1),(1,2), (1,3), (2,3), (1,2,3)....)
		expansive_max=N:
			Generate every possible combination up to some max number 
	"""
	# GET ALL INDIVIDUALS
	individuals = Individual.objects.all().order_by('ind_uuid')[0:4]
	
	# SET reasonable DEFAULT:
#	if option is None:
#		option = 'expansive_max'
#		if N is None:
#			N=len(individuals)/2
	if option is None:
		option='each'
		
	# MAKE SURE NOT TO OVERSPECIFY N
	if N:
		if N>len(individuals):
			N = len(individuals) 
			
	# GET LIST OF ALL IDs
	id_list = []
	for id in individuals:
		id_list.append(id.ind_uuid)
		
	# PROCESS LIST
	if option=='each':
		results = list(combinations(id_list,1))  
		
	if option=='combo':
		if N is None:
			raise Exception("You must specify a value of N")
		results = list(combinations(id_list,N))

	if option=='expansive':
		results = list(powerset(id_list))
		
	if option=='expansive_max':
		results = []
		if N is None:
			raise Exception("You must specify a value of N")
		pset = list(powerset(id_list))
		# Remove lenght > N
		for elem in pset:
			if len(elem)<=N:
				results.append(elem)
		
	return results



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
		# options = {'each', 'combo', 'expansive', 'expansive_max'
		# 0<N<# of individuals
		Y0=generate_initial_infected(option=None, N=None)
		timestep = [0.1]
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
	print "beta, gamma, alpha, Y0, timestep, max_time, t_min_filter, t_max_filter, multiplicity"
	beta, gamma, alpha, Y0, timestep, max_time, t_min_filter, t_max_filter, multiplicity = set_initial_parameters(dry_run)
	parameter_set = list(product(beta, gamma, alpha, Y0, timestep, max_time, t_min_filter, t_max_filter))
	full_parameter_set = multiplicity*parameter_set
	return full_parameter_set
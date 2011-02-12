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

####################################
# ** IMPORT DEPENDENCIES
from django.db.models import Max, Min, Q
import uuid
from simulations.models import *
from simulations import infections, recovery

from numpy.random import rand
from numpy import exp

#def program_si(beta, gamma, alpha, Y0, timestep, max_time, t_min_filter, t_max_filter, infection_function):
def program_si(infection_function, recovery_function, set_of_parameters, *args, **kwargs):
	"""
	Code to produce a single SI time series based on input parameters
	"""
	if kwargs.get('dryrun'):
		print 'DRY RUN: %s, %s, %s' % (infection_function, recovery_function, set_of_parameters)
		return None
	elif kwargs.get('test_number'):
		print 'TESTING: %s, %s, %s' % (infection_function, recovery_function, set_of_parameters)
		return None
	
	# ** LOAD INFECTION FUNCTION
	infection_function = getattr(infections, infection_function)
	# ** LOAD RECOVERY FUNCTION (NOT USED IN THIS SIMULATION)
	recovery_function = getattr(recovery, recovery_function)
	
	# WARNING: UNPACK PARAMETERS.  MUST BE USED IN CONJUCTION WITH simulate.main(): make sure to pass in correct arguments
	beta, Y0, t_min_filter, t_max_filter = set_of_parameters
	
	S = []
	I = []
	T = []
	
	# LOAD DATA BASED ON filters
	min_duration = Interaction.objects.aggregate(Min('duration')).get('duration__min')
	max_duration = Interaction.objects.aggregate(Max('duration')).get('duration__max')
	
	# SET FILTER TO ZERO IF NOT SPECIFIED
	if t_min_filter is None:
		t_min_filter = 0
	# SET FILTER TO MAX IF NOT SPECIFIED		
	if t_max_filter is None:
		t_max_filter = max_duration
	# RAISE ERROR IF FILTERS WOULD EXCLUDE ALL DATA
	if t_max_filter < min_duration:
		raise Exception("t_max_filter too small: min duration = %s" % min_duration)
	if t_min_filter > max_duration:
		raise Exception("t_min_filter too large: max duration = %s" % max_duration)
	
	# GET ALL INTERACTIONS SATISFYING DURATION CONSTRAINTS	
	all_valid_interactions = Interaction.objects.filter(duration__gte=t_min_filter, duration__lte=t_max_filter).order_by('time_start')
	
	# MAKE SURE THAT THE SET OF INITIAL INFECTEDS IS A TUPLE, EVEN IF ONLY ONE PASSED IN
	if isinstance(Y0,int):
		Y0=(Y0,)
	
	# SET INITIAL S, I status for all individuals
	initial_infection_start_time = Interaction.objects.aggregate(Min('time_start')).get('time_start__min')
	for individual in Individual.objects.all():
		# SET INFECTED
		if individual.ind_uuid in Y0:
			individual.is_infected = True
			infection_network, in_created = InfectionNetwork.objects.get_or_create(individual=individual,infection_start=initial_infection_start_time)
		else:
			individual.is_infected = False
		individual.save()

	####################################
	####################################
	#	MODIFY PROGRAM BELOW HERE      #
	####################################
	####################################
	
	# MAIN LOOP: CALCULATE INFECTIONS
	for interaction in all_valid_interactions:
		i1 = interaction.individual_one
		i2 = interaction.individual_two
		if i1.is_infected and not i2.is_infected:
			# CALCULATE q
			q = infection_function(interaction.duration, beta)
			# DETERMINE IF INFECTION OCCURRED
			if q > rand():
				i2.is_infected=True
				i2.save()

				################################
				# ** CAPTURE INFECTION NETWORK
				time_of_infection = interaction.time_start+(interaction.duration/2) # IS THIS CORRECT?
				i1_inf_net, in1_created = InfectionNetwork.objects.get_or_create(individual=i1)
				i2_inf_net, in1_created = InfectionNetwork.objects.get_or_create(parent=i1_inf_net,individual=i2,infection_start=time_of_infection)
			
		elif not i1.is_infected and i2.is_infected:
			# CALCULATE q
			q = infection_function(interaction.duration, beta)
			# DETERMINE IF INFECTION OCCURRED
			if q > rand():
				i1.is_infected=True
				i1.save()

				################################
				# ** CAPTURE INFECTION NETWORK
				time_of_infection = interaction.time_start+(interaction.duration/2) # IS THIS CORRECT?
				i2_inf_net, in1_created = InfectionNetwork.objects.get_or_create(individual=i2)
				i1_inf_net, in1_created = InfectionNetwork.objects.get_or_create(parent=i2_inf_net,individual=i1,infection_start=time_of_infection)

		# UPDATE S I T
		S.append(Individual.objects.filter(is_infected=False).count())
		I.append(Individual.objects.filter(is_infected=True).count())
		T.append(interaction.time_start)

	# DERIVATIVE CALCULATIONS ON time series data  

	# Generate unique id for run
	sim_uuid = str(uuid.uuid4())[0:30]

	# CREATE DICTIONARY TO LOAD VARIABLE SIMRUN PARAMETERS
	simulation_dict = {
					'beta':beta,
					't_min_filter':t_min_filter,
					't_max_filter':t_max_filter,
					}
	# STORE PARAMETERS
	sim_run = SimRun.objects.create(
								sim_uuid=sim_uuid,
								infection_function=infection_function,
								 **simulation_dict)
		
	# STORE INITIAL INFECTED
	for ind_uuid in Y0:
		individual = Individual.objects.get(ind_uuid=ind_uuid)
		ii = InitialInfected.objects.create(sim_run=sim_run, individual_infected=individual)

	# STORE S, I, T
	for s, i, t in zip(S,I,T):
		SimTimeSeries.objects.create(sim_run=sim_run,susceptible=s,infected=i,t=t)




def program_sir_sendhome(infection_function, recovery_function, set_of_parameters, *args, **kwargs):
	"""
	Code to produce a single SI time series based on input parameters
	"""
	if kwargs.get('dryrun'):
		print 'DRY RUN: %s, %s, %s' % (infection_function, recovery_function, set_of_parameters)
		return None

	elif kwargs.get('test_number'):
		print 'TESTING: %s, %s, %s' % (infection_function, recovery_function, set_of_parameters)
		return None
	
	# ** LOAD INFECTION FUNCTION
	infection_function = getattr(infections, infection_function)
	# ** LOAD RECOVERY FUNCTION (NOT USED IN THIS SIMULATION)
	recovery_function = getattr(recovery, recovery_function)
	
	# WARNING: UNPACK PARAMETERS.  MUST BE USED IN CONJUCTION WITH simulate.main(): make sure to pass in correct arguments
	beta, nu, Y0, t_min_filter, t_max_filter = set_of_parameters
	
	S = []
	I = []
	T = []
	
	# LOAD DATA BASED ON filters
	min_duration = Interaction.objects.aggregate(Min('duration')).get('duration__min')
	max_duration = Interaction.objects.aggregate(Max('duration')).get('duration__max')
	
	# SET FILTER TO ZERO IF NOT SPECIFIED
	if t_min_filter is None:
		t_min_filter = 0
	# SET FILTER TO MAX IF NOT SPECIFIED		
	if t_max_filter is None:
		t_max_filter = max_duration
	# RAISE ERROR IF FILTERS WOULD EXCLUDE ALL DATA
	if t_max_filter < min_duration:
		raise Exception("t_max_filter too small: min duration = %s" % min_duration)
	if t_min_filter > max_duration:
		raise Exception("t_min_filter too large: max duration = %s" % max_duration)
	
	# GET ALL INTERACTIONS SATISFYING DURATION CONSTRAINTS	
	all_valid_interactions = Interaction.objects.filter(duration__gte=t_min_filter, duration__lte=t_max_filter).order_by('time_start')
	
	# MAKE SURE THAT THE SET OF INITIAL INFECTEDS IS A TUPLE, EVEN IF ONLY ONE PASSED IN
	if isinstance(Y0,int):
		Y0=(Y0,)
	
	# SET INITIAL S, I status for all individuals
	initial_infection_start_time = Interaction.objects.aggregate(Min('time_start')).get('time_start__min')
	for individual in Individual.objects.all():
		# SET INFECTED
		if individual.ind_uuid in Y0:
			individual.is_infected = True
			infection_network, in_created = InfectionNetwork.objects.get_or_create(individual=individual,infection_start=initial_infection_start_time)
		else:
			individual.is_infected = False
		individual.save()
	####################################
	####################################
	#	MODIFY PROGRAM BELOW HERE      #
	####################################
	####################################

	# MAIN LOOP: CALCULATE INFECTIONS
	disallowed_interactions = []
	for interaction in all_valid_interactions:
		# REMOVE INTERACTIONS DURING TIME WHEN INDIVIDUALS ARE AT HOME
		if interaction in disallowed_interactions:
			print 'removed: %s' % interaction
			continue
		
		i1 = interaction.individual_one
		i2 = interaction.individual_two
		if i1.is_infected and not i2.is_infected:
			# CALCULATE q
			q = infection_function(interaction.duration, beta)
			# DETERMINE IF INFECTION OCCURRED
			if q > rand():
				i2.is_infected=True
				i2.save()

				################################
				# ** CAPTURE INFECTION NETWORK
				time_of_infection = interaction.time_start+(interaction.duration/2) # IS THIS CORRECT?
				duration_of_infection = recovery_function(nu)
				time_of_recovery  = time_of_infection+duration_of_infection

				i1_inf_net, in1_created = InfectionNetwork.objects.get_or_create(individual=i1)
				i2_inf_net, in1_created = InfectionNetwork.objects.get_or_create(parent=i1_inf_net,individual=i2,infection_start=time_of_infection, infection_stop=time_of_recovery)
				
				####################################################
				# ** REMOVE INTERACTIONS OCCURRING IN THIS PERIOD
				removed_interaction = Interaction.objects.filter(
					Q(time_start__gte=time_of_infection),
					Q(time_stop__lte=time_of_recovery),
					Q(individual_one=i1) | Q(individual_two=i1),
				)				
				disallowed_interactions+=removed_interactions
				#####################################################
		elif not i1.is_infected and i2.is_infected:
			# CALCULATE q
			q = infection_function(interaction.duration, beta)
			# DETERMINE IF INFECTION OCCURRED
			if q > rand():
				i1.is_infected=True
				i1.save()

				################################
				# ** CAPTURE INFECTION NETWORK
				time_of_infection = interaction.time_start+(interaction.duration/2) # IS THIS CORRECT?
				duration_of_infection = recovery_fuction(nu)
				time_of_recovery  = time_of_infection+duration_of_infection

				i2_inf_net, in1_created = InfectionNetwork.objects.get_or_create(individual=i2)
				i1_inf_net, in1_created = InfectionNetwork.objects.get_or_create(parent=i2_inf_net,individual=i1,infection_start=time_of_infection, infection_stop=time_of_recovery)

				####################################################
				# ** REMOVE INTERACTIONS OCCURRING IN THIS PERIOD
				removed_interaction = Interaction.objects.filter(
					Q(time_start__gte=time_of_infection),
					Q(time_stop__lte=time_of_recovery),
					Q(individual_one=i1) | Q(individual_two=i1),
				)				
				disallowed_interactions+=removed_interactions
				#####################################################


		# UPDATE S I T
		S.append(Individual.objects.filter(is_infected=False).count())
		I.append(Individual.objects.filter(is_infected=True).count())
		T.append(interaction.time_start)

	# DERIVATIVE CALCULATIONS ON time series data  

	# Generate unique id for run
	sim_uuid = str(uuid.uuid4())[0:30]

	# CREATE DICTIONARY TO LOAD VARIABLE SIMRUN PARAMETERS
	simulation_dict = {
					'beta':beta,
					't_min_filter':t_min_filter,
					't_max_filter':t_max_filter,
					}
	# STORE PARAMETERS
	sim_run = SimRun.objects.create(
								sim_uuid=sim_uuid,
								infection_function=infection_function,
								 **simulation_dict)
		
	# STORE INITIAL INFECTED
	for ind_uuid in Y0:
		individual = Individual.objects.get(ind_uuid=ind_uuid)
		ii = InitialInfected.objects.create(sim_run=sim_run, individual_infected=individual)

	# STORE S, I, T
	for s, i, t in zip(S,I,T):
		SimTimeSeries.objects.create(sim_run=sim_run,susceptible=s,infected=i,t=t)





def program_sir_sendhome_old(beta, gamma, alpha, Y0, timestep, max_time, t_min_filter, t_max_filter, infection_function):
	"""
	Code to produce a single SIR time series based on input parameters
	Send individuals home == remove interactions that occur during the time they are at home
	"""
	S = []
	I = []
	T = []
	# LOAD DATA BASED ON filters
	min_duration = Interaction.objects.aggregate(Min('duration')).get('duration__min')
	max_duration = Interaction.objects.aggregate(Max('duration')).get('duration__max')
	if t_min_filter is None:
		t_min_filter = 0
	if t_max_filter is None:
		t_max_filter = max_duration
		 
	if t_max_filter < min_duration:
		raise Exception("t_max_filter too small: min duration = %s" % min_duration)
	if t_min_filter > max_duration:
		raise Exception("t_min_filter too large: max duration = %s" % max_duration)

	
	# GET ALL INTERACTIONS SATISFYING DURATION CONSTRAINTS	
	all_valid_interactions = Interaction.objects.filter(duration__gte=t_min_filter, duration__lte=t_max_filter).order_by('time_start')
	
	# MAKE SURE THAT THE SET OF INITIAL INFECTEDS IS A TUPLE, EVEN IF ONLY ONE PASSED IN
	if isinstance(Y0,int):
		Y0=(Y0,)
	
	# SET INITIAL S, I status for all individuals
	for individual in Individual.objects.all():
		# SET INFECTED
		if individual.ind_uuid in Y0:
			individual.is_infected = True
		else:
			individual.is_infected = False
		individual.save()
	
	# MAIN LOOP: CALCULATE INFECTIONS
	disallowed_interactions = []
	for interaction in all_valid_interactions:
		
		# REMOVE INTERACTIONS DURING TIME WHEN INDIVIDUALS ARE AT HOME
		if interaction in disallowed_interactions:
			continue
		
		i1 = interaction.individual_one
		i2 = interaction.individual_two
		if i1.is_infected and not i2.is_infected:
			# LOAD FUNCTION (i.e. Q = 1-exp(-duration*beta)) 
			Q = getattr(infections,infection_function)
			# CALCULATE q
			q = Q(interaction.duration, beta)
			# DETERMINE IF INFECTION OCCURRED
			if q > rand():
				i2.is_infected=True
				i2.save()
			
		elif not i1.is_infected and i2.is_infected:
			# LOAD FUNCTION (i.e. Q = 1-exp(-duration*beta)) 
			Q = getattr(infections,infection_function)
			# CALCULATE q
			q = Q(interaction.duration, beta)
			# DETERMINE IF INFECTION OCCURRED
			if q > rand():
				i1.is_infected=True
				i1.save()

		# UPDATE S I T
		S.append(Individual.objects.filter(is_infected=False).count())
		I.append(Individual.objects.filter(is_infected=True).count())
		T.append(interaction.time_start)
		
		# REMOVE INDIVIDUALS, SET
	return S, I, T 

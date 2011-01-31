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
from django.db.models import Max, Min
import uuid
from simulations.models import *
from simulations import infections

from numpy.random import rand
from numpy import exp

def program_sir(beta, gamma, alpha, Y0, timestep, max_time, t_min_filter, t_max_filter, infection_function):
	"""
	Code to produce a single SIR time series based on input parameters
	S = [9,9,9,9,8,8,7,6,5,0]
	I = [0,0,0,0,1,1,2,3,4,9]
	T = [1,5,10,11,14,18,19,20,21,22]

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
	
	# SANITY CHECK
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
	for interaction in all_valid_interactions:
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
	return S, I, T 



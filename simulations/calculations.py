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
import uuid
from simulations.models import *
from simulations import initial_processing

def program_sir(beta, gamma, alpha, Y0, timestep, max_time, t_min_filter, t_max_filter):
	S = [9,9,9,9,8,8,7,6,5,0]
	I = [0,0,0,0,1,1,2,3,4,9]
	T = [1,5,10,11,14,18,19,20,21,22]
	return S, I, T 


def single_run():
	pass

if __name__=='__main__':
	function_to_run = 'load_individuals'
	program_to_run = getattr(initial_processing, function_to_run)
	program_to_run()
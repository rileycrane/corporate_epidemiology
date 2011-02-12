# DEFINE THE VARIOUS INFECTION FUNCTIONS HERE
# 	You can then pass them into the simulation() call in simulations/simulate.py
from numpy import exp

def standard_infection(duration,beta,*args, **kwargs):
	"""
	defines the standard infection calculation
	"""
	Q = 1 - exp(-duration*beta)
	return Q

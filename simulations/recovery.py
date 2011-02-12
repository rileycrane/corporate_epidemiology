from __future__ import division
# DEFINE THE VARIOUS RECOVERY FUNCTIONS HERE
# 	You can then pass them into the simulation() call in simulations/simulate.py
from numpy import exp

def standard_recovery(nu, *args, **kwargs):
	"""
	Calculate how long an individual is sick
	Ellen and Leon should help us with this
	D = duration of of infection
	nu = rate of recovery = 1/D
	
	"""
	return 1/nu

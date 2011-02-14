###################################
# RULES FOR SENDING PEOPLE HOME

from __future__ import division
# DEFINE THE VARIOUS RECOVERY FUNCTIONS HERE
# 	You can then pass them into the simulation() call in simulations/simulate.py
from numpy import exp

def standard_sendhome(alpha, *args, **kwargs):
	"""
	Calculate when to send someone home
	NOTE: 0 < alpha < 1 : the fraction of total infection period to wait before going home 
	"""
	if kwargs.get('duration'):
		return alpha*kwargs.get('duration')
	else:
		return alpha

from numpy import exp

def standard(duration,beta,*args, **kwargs):
	"""
	defines the standard infection
	"""
	Q = 1 - exp(-duration*beta)
	return Q
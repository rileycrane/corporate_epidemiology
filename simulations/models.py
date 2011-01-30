from django.db import models


class SimRun(models.Model):
	"""
	Keeps track of the result of each calculation
	"""
	sim_uuid = models.CharField(max_length=50)
	calculation_name = models.CharField(max_length=200,blank=True,null=True)
	alpha = models.FloatField(blank=True,null=True)
	beta  = models.FloatField(blank=True,null=True)
	gamma = models.FloatField(blank=True,null=True)
	timestep = models.FloatField(blank=True,null=True)
	max_time = models.IntegerField(blank=True,null=True) 
	t_min_filter = models.FloatField(blank=True,null=True) # Time in seconds
	t_max_filter = models.FloatField(blank=True,null=True) # Time in seconds
	created_at = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		#return self.uuid
		return "%s, %s: %s" % (self.calculation_name,self.created_at,self.sim_uuid)

	def get_absolute_url(self):
		return "/simulations/%s/" % self.sim_uuid

class SimTimeSeries(models.Model):
	"""
	Stores one value in the time series, connected to the parameters of the SimRun
	"""
	sim_run     = models.ForeignKey(SimRun)
	susceptible = models.IntegerField()
	infected    = models.IntegerField()
	t           = models.FloatField()

class Individual(models.Model):
	"""
	Defines each individual according to their id
	as defined in ir_interactions.txt
	initial_data in fixtures
	"""
	ind_uuid = models.IntegerField(unique=True)
	def __unicode__(self):
		#return self.uuid
		return "%s" % self.ind_uuid

class InitialInfected(models.Model):
	"""
	This keeps track of the set of individuals infected 
	during each simulation run.  Can be accessed with
	SimRun.initialinfected_set.all()
	"""
	sim_run = models.ForeignKey(SimRun)
	individual_infected = models.ForeignKey(Individual) 
#	def __unicode__(self):
#		return sim_run.uuid

class Interaction(models.Model):
	"""
	Captures each of the interactions amongst the individuals
	as measured in ir_interactions
	initial_data in fixtures
	"""
	individual_one   = models.ForeignKey(Individual, related_name='individual_one')
	individual_two   = models.ForeignKey(Individual, related_name='individual_two')
	time_start     = models.IntegerField()
	time_stop      = models.IntegerField()
	duration       = models.FloatField()
	# Do the pairwise interactions overlap with other interactions involving the same individuals?
	overlap        = models.BooleanField(default=False)
	class Meta:
		unique_together = (("individual_one", "individual_two", "time_start"),)
	def __unicode__(self):
		#return self.uuid
		return "%s, %s: %s" % (self.individual_one.ind_uuid, self.individual_two.ind_uuid, self.duration)
	
#	def __unicode__(self):
#		return "%s & %s: dt=%s" % (self.individual_one.uuid, self.individual_two.uuid, self.duration)

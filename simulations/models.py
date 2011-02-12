from django.db import models
from django.db.models import Max
from mptt.models import MPTTModel
###########################################################
# ** BUILD BASE CLASS FOR SIMULATION OBJECT
#		ALLOW OTHERS TO SUBCLASS FOR SPECIFIC SIMULATIONS 
#class SimBasic(models.Model):
#	"""
#	Basic class for all simulations
#	"""
#	sim_uuid = models.CharField(max_length=50)
#	infection_function = models.CharField(max_length=200,blank=True,null=True)
#	created_at = models.DateTimeField(auto_now=True)
#
#	def initial_number_infections(self):
#		"""
#		Return the number of individuals initially infected
#		"""
#		return self.initialinfected_set.count()

class SimRun(models.Model):
	"""
	Keeps track of the result of each calculation
	"""
	sim_uuid           = models.CharField(max_length=50)
	infection_function = models.CharField(max_length=200,blank=True,null=True)
	recovery_function  = models.CharField(max_length=200,blank=True,null=True)
	alpha              = models.FloatField(blank=True,null=True)
	beta               = models.FloatField(blank=True,null=True)
	gamma              = models.FloatField(blank=True,null=True)
	timestep           = models.FloatField(blank=True,null=True)
	max_time           = models.IntegerField(blank=True,null=True) 
	t_min_filter       = models.FloatField(blank=True,null=True) # 
	t_max_filter       = models.FloatField(blank=True,null=True) # 
	created_at         = models.DateTimeField(auto_now=True)

	def initial_number_infections(self):
		"""
		Return the number of individuals initially infected
		"""
		return self.initialinfected_set.count()
	
	def final_size(self):
		"""
		Return the final size of the epidemic
		"""
		return self.simtimeseries_set.aggregate(Max('infected')).get('infected__max')
	
	def interaction_network(self):
		"""
		Return the interactions used in this model after applying filter
		"""
		return Interaction.objects.filter(duration__gte=self.t_min_filter, duration__lte=self.t_max_filter)

	def __unicode__(self):
		"""
		Returns a string associated with this calculation
		"""
		return "%s, %s: %s" % (self.infection_function,self.created_at,self.sim_uuid)

	def get_absolute_url(self):
		"""
		Returns a url pointing to the visualization of the epidemic
		"""
		return "/simulations/%s/" % self.sim_uuid


class SimTimeSeries(models.Model):
	"""
	Stores one value in the time series, connected to the parameters of the SimRun
	"""
	sim_run     = models.ForeignKey(SimRun) # Link to the simulation run
	susceptible = models.IntegerField() # Count of number susceptible
	infected    = models.IntegerField() # Count of number infected
	t           = models.FloatField()   # Time 

class Individual(models.Model):
	"""
	Defines each individual according to their id
	as defined in ir_interactions.txt
	initial_data in fixtures
	"""
	ind_uuid    = models.IntegerField(unique=True)
	is_infected = models.BooleanField(default=False)
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
	def __unicode__(self):
		return "%s: %s" % (self.sim_run.sim_uuid, self.individual_infected.ind_uuid)

class InfectionNetwork(MPTTModel):
	"""
	Store adjacency lists, trees
	"""
	parent          = models.ForeignKey('self', null=True, blank=True, related_name='children')
	individual      = models.ForeignKey(Individual,unique=True)
	infection_start = models.IntegerField(blank=True, null=True)
	infection_stop  = models.IntegerField(blank=True, null=True)
	duration        = models.FloatField(blank=True, null=True)

	def __unicode__(self):
		if self.parent and self.infection_stop:
			return "%s: infected by %s @ %s | recovered @ %s" % (self.individual.ind_uuid, self.parent.individual.ind_uuid,self.infection_start, self.infection_stop)
		elif self.parent:
			return "%s: infected by %s @ %s" % (self.individual.ind_uuid, self.parent.individual.ind_uuid,self.infection_start)
		else:
			return "%s: initial seed" % (self.individual.ind_uuid)



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

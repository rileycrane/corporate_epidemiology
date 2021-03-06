from __future__ import division
from django.conf import settings
from django.db import models
from django.db.models import Max
from mptt.models import MPTTModel
import pygraphviz as pgv
import pdb

PATH_TO_CORP_EPI = getattr(settings, 'PATH_TO_CORP_EPI','')
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
	sendhome_function  = models.CharField(max_length=200,blank=True,null=True)
	beta               = models.FloatField(blank=True,null=True) # Transmission Rate
	gamma              = models.FloatField(blank=True,null=True) # Recovery Rate
	alpha              = models.FloatField(blank=True,null=True) # Send Home Parameter
	t_min_filter       = models.FloatField(blank=True,null=True) # 
	t_max_filter       = models.FloatField(blank=True,null=True) # 
	created_at         = models.DateTimeField(auto_now=True)

	def get_initial_infected_individuals(self):
		"""
		Get set of individuals that were infected at beginning of simulation
		"""
		initial_individuals_infected = []
		for infection in self.infectionevent_set.all():
			if infection.vector is None:
				initial_individuals_infected.append(infection.target)
		return initial_individuals_infected

	def number_initial_infections(self):
		"""
		Return the number of individuals initially infected
		"""
		return self.infectionevent_set.filter(interaction=None).count()
	
	def number_secondary_infections(self):
		"""
		Return the total number of infection events, discounted by the number of initial infections
		"""
		#return self.simtimeseries_set.aggregate(Max('infected')).get('infected__max')
		return self.infectionevent_set.count()-self.number_initial_infections()
	
	def percent_infected(self):
		"""
		Calculate what fraction of the total population was infected at some point during the outbreak
		"""
		#individuals = Individual.objects.all()
		infected_individuals = self.get_initial_infected_individuals()
		for infection_event in self.infectionevent_set.all():
			if infection_event.target not in infected_individuals:
				infected_individuals.append(infection_event.target)
		
		infected_count = len(infected_individuals)
		total_count    = Individual.objects.count()
		percent_infected = infected_count/total_count
		return percent_infected
	
	def interaction_network(self):
		"""
		Return the interactions used in this model after applying filter
		"""
		return Interaction.objects.filter(duration__gte=self.t_min_filter, duration__lte=self.t_max_filter)

	def to_adjacency(self):
		"""
		Returns adjacency list in the following format
			infecter, infectee, time_start_infection, time_sent_home, time_return_work, time_stop_infection
		"""
		adjacency_list = []
		for infection in self.infectionevent_set.all():
			vector               = infection.vector
			target               = infection.target
			time_start_infection = infection.time_start_infection
			time_stop_infection  = infection.time_stop_infection
			time_start_symptoms  = infection.time_start_symptoms
			time_stop_symptoms   = infection.time_stop_symptoms
			
			adjacency_list.append(
					'%s, %s, %s, %s, %s, %s' % (vector, target, time_start_infection, time_start_symptoms, time_stop_symptoms, time_stop_infection)
					)
		return adjacency_list

	def to_graph(self):
		"""
		Create a graph
		"""
		dot_name = '%s/media/graphs/%s.dot' % (PATH_TO_CORP_EPI, self.sim_uuid)
		img_name = '%s/media/graphs/%s.png' % (PATH_TO_CORP_EPI, self.sim_uuid)
		dot_name = dot_name.replace('-','')
		img_name = img_name.replace('-','')
		dot_file = open(dot_name,'w')
		img_file = open(img_name,'w')
		#dot_name = 'd.dot'
		#img_name = 'i.png'

		A=pgv.AGraph()
		for infection_event in self.infectionevent_set.all():
			target = infection_event.target
			vector = infection_event.vector
			if target:
				target_id = target.ind_uuid
			else:
				target_id = 0
			if vector:
				vector_id = vector.ind_uuid
			else:
				vector_id = 0
			A.add_edge(target_id,vector_id)
		A.write(path=dot_file) # write to simple.dot
		B=pgv.AGraph(dot_name) # create a new graph from file
		B.layout() # layout with default (neato)
		B.draw(path=img_file) # draw png
		
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


#class SimTimeSeries(models.Model):
#	"""
#	Stores one value in the time series, connected to the parameters of the SimRun
#	"""
#	sim_run     = models.ForeignKey(SimRun) # Link to the simulation run
#	susceptible = models.IntegerField() # Count of number susceptible
#	infected    = models.IntegerField() # Count of number infected
#	t           = models.FloatField()   # Time 

class Individual(models.Model):
	"""
	Defines each individual according to their id
	as defined in ir_interactions.txt
	initial_data in fixtures
	"""
	ind_uuid    = models.IntegerField(unique=True)
	
	def is_infected(self):
		"""
		Lookup infection status
		"""
		return self.infectionstatus_set.get().is_infected
	
	def is_at_home_now(self, time_now):
		"""
		calculate whether or not an individual is at home at the start of this interaction
		"""
		# GET TIME INDIVIDUAL RETURNS AT
		at_home_from  = self.infectionstatus_set.get().is_at_home_from
		at_home_until = self.infectionstatus_set.get().is_at_home_until
		
		if time_now > at_home_from and time_now < at_home_until:
			return True
		else:
			return False

	def __unicode__(self):
		#return self.uuid
		return "%s" % self.ind_uuid


class InfectionStatus(models.Model):
	"""
	Holds state information for individuals
	"""
	individual       = models.ForeignKey(Individual, unique=True)
	is_infected      = models.BooleanField(default=False)
	is_at_home_from  = models.IntegerField(blank=True, null=True)
	is_at_home_until = models.IntegerField(blank=True, null=True) # if time > until, reset is_infected to False
	#is_initial       = models.BooleanField(default=False) 
	#has_symptoms     = models.BooleanField(default=False)
	def __unicode__(self):
		"""
		Returns a string associated with this calculation
		"""
		return "%s, %s: %s" % (self.individual,self.is_infected,self.is_at_home_until)


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
		
	def is_not_allowed(self):
		"""
		This method prevents disallowed interactions
			i.e. those which occur when the infected individual is sent home
		This method also resets InfectionStatus once the time has passed
		"""
		###########################
		# SET DEFAULT RESPONSE
		response = False
		
		##############################################
		# GET INFECTION STATUS FOR BOTH INDIVIDUALS
		infection_status_one = self.individual_one.infectionstatus_set.get()
		infection_status_two = self.individual_two.infectionstatus_set.get()

		##########################################################################
		# UPDATE INFECTION STATE AT BEGINNING OF INTERACTION
		#	Fast-forwards the individual's infection status to the current time
		#	This is necessary since we are not 'time-stepping'
		if self.individual_one.is_infected() and self.individual_two.is_infected():
			# UPDATE ONE
			if self.time_start > infection_status_one.is_at_home_until:
				infection_status_one.is_infected=False
				infection_status_one.save()
			# UPDATE TWO
			if self.time_start > infection_status_two.is_at_home_until:
				infection_status_two.is_infected=False
				infection_status_two.save()

		elif self.individual_one.is_infected():
			# UPDATE ONE
			if self.time_start > infection_status_one.is_at_home_until:
				infection_status_one.is_infected=False
				infection_status_one.save()
		elif self.individual_two.is_infected():
			# UPDATE TWO
			if self.time_start > infection_status_two.is_at_home_until:
				infection_status_two.is_infected=False
				infection_status_two.save()
		#############################################################################

		######################################
		# ** AFTER UPDATING TO CURRENT TIME:
		# BOTH INFECTED
		if infection_status_one.is_infected and infection_status_two.is_infected:
			return True
		# NEITHER INFECTED
		elif not infection_status_one.is_infected and not infection_status_two.is_infected:
			return True
		# ONE OF THEM IS INFECTED, CHECK IF THEY ARE AT HOME
		else:
			# INDIVIDUAL ONE infected
			if infection_status_one.is_infected:
				if self.individual_one.is_at_home_now(self.time_start):
					return True # SKIP INTERACTION
				else:
					return False# INFECTED, AND AT WORK
			# INDIVIDUAL TWO infected
			else:
				if self.individual_two.is_at_home_now(self.time_start):
					return True # SKIP INTERACTION
				else:
					return False# INFECTED, AND AT WORK
				

	def __unicode__(self):
		#return self.uuid
		return "%s, %s: %s" % (self.individual_one.ind_uuid, self.individual_two.ind_uuid, self.duration)

class InfectionEvent(models.Model):
	sim_run         = models.ForeignKey(SimRun)
	interaction     = models.ForeignKey(Interaction, blank=True, null=True)
	vector          = models.ForeignKey(Individual, related_name='sick_person', blank=True, null=True)
	target          = models.ForeignKey(Individual, related_name='about_to_be_sick')
	time_start_infection = models.IntegerField(blank=True, null=True)
	time_stop_infection  = models.IntegerField(blank=True, null=True)
	time_start_symptoms  = models.IntegerField(blank=True, null=True)
	time_stop_symptoms   = models.IntegerField(blank=True, null=True)
	duration_symptoms    = models.FloatField(blank=True, null=True)
	duration_infection   = models.FloatField(blank=True, null=True)
	def __unicode__(self):
		#return self.uuid
		return "%s infected by %s @ %s for %s" % (self.target, self.vector, self.time_start_infection, self.duration_symptoms)

#class Riley(models.Model):
#	sim_run         = models.ForeignKey(SimRun)
#	interaction     = models.ForeignKey(Interaction)
#	target          = models.ForeignKey(Individual, related_name='target')
#	time_start_infection = models.IntegerField(blank=True, null=True)
#	time_stop_infection  = models.IntegerField(blank=True, null=True)
#	time_start_symptoms  = models.IntegerField(blank=True, null=True)
#	time_stop_symptoms   = models.IntegerField(blank=True, null=True)
#	duration        = models.FloatField(blank=True, null=True)

#class InitialInfected(models.Model):
#	"""
#	This keeps track of the set of individuals infected 
#	during each simulation run.  Can be accessed with
#	SimRun.initialinfected_set.all()
#	"""
#	sim_run = models.ForeignKey(SimRun)
#	individual_infected = models.ForeignKey(Individual) 
#	def __unicode__(self):
#		return "%s: %s" % (self.sim_run.sim_uuid, self.individual_infected.ind_uuid)
#
#class InfectionNetwork(MPTTModel):
#	"""
#	Store adjacency lists, trees
#	"""
#	parent          = models.ForeignKey('self', null=True, blank=True, related_name='children')
#	individual      = models.ForeignKey(Individual,unique=True)
#	infection_start = models.IntegerField(blank=True, null=True)
#	infection_stop  = models.IntegerField(blank=True, null=True)
#	duration        = models.FloatField(blank=True, null=True)
#
#	def __unicode__(self):
#		if self.parent and self.infection_stop:
#			return "%s: infected by %s @ %s | recovered @ %s" % (self.individual.ind_uuid, self.parent.individual.ind_uuid,self.infection_start, self.infection_stop)
#		elif self.parent:
#			return "%s: infected by %s @ %s" % (self.individual.ind_uuid, self.parent.individual.ind_uuid,self.infection_start)
#		else:
#			return "%s: initial seed" % (self.individual.ind_uuid)

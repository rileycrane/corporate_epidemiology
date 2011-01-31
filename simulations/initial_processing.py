# FUNCTIONS TO LOAD INITIAL DATA
from __future__ import division
import os
import numpy
ROOT_PATH = os.path.dirname(__file__)

# IMPORT DATA MODELS
from simulations.models import *

def load_individuals():
	"""
	PARSE ir_interactions.txt and load data to models
	"""
	# DEFINE PATH TO FILE
	data_file  = os.path.join(ROOT_PATH,'data','ir_interactions.txt')

	# GET MIN/MAX TIMES
	data_array = numpy.loadtxt(data_file, delimiter="\t")
	min_time   = numpy.min(data_array[:,2])
	max_time   = numpy.max(data_array[:,3])

	# OPEN FILE
	file_stream = open(data_file,'r')
	
	# READ FILE INTO LIST
	content_list = file_stream.readlines()
	
	# PROCESS LIST
	for single_interaction in content_list:
		# Extract data from line
		id_one, id_two, time_start, time_stop = single_interaction.split()
		
		# GET OR CREATE id one in database 
		individual_one, id_one_created = Individual.objects.get_or_create(ind_uuid=id_one)
		# GET OR CREATE id two in database
		individual_two, id_two_created = Individual.objects.get_or_create(ind_uuid=id_two)
		
		# GET OR CREATE INTERACTION in database
		interaction = Interaction()
		interaction.individual_one = individual_one 
		interaction.individual_two = individual_two
		time_start = int(numpy.float64(time_start)/374400) # secs since start
		interaction.time_start     = time_start
		time_stop = int(numpy.float64(time_stop)/374400) # secs since start
		interaction.time_stop      = time_stop
		interaction.duration       = time_stop-time_start
		try:
			interaction.save()
		except:
			pass

if __name__=='__main__':
	load_individuals()
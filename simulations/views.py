from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.views.generic.simple import direct_to_template
from simulations.models import *

def get_simulation_data(sim_uuid):
	"""
	Gets daily susceptible and shows those which are > level 1 --> word of mouth
	"""
	try:
		sim_run = SimRun.objects.get(sim_uuid=sim_uuid)
	except:
		return HttpResponse("View Does Not Exist")
	
	time_series = SimTimeSeries.objects.filter(sim_run=sim_run).order_by('t')
	number_of_rows = len(time_series)
	
	visualization_data = """
		data.addColumn('string', 'Time');
		data.addColumn('number', 'Susceptible');
		data.addColumn('number', 'Infected');
		data.addRows(%s);\n""" % number_of_rows
	
	counter = -1
	for element in time_series:
		counter+=1
		try:
			visualization_data+="""data.setValue(%s,0,'%s');\ndata.setValue(%s,1,%s);\ndata.setValue(%s,2,%s);\n""" % (counter, element.t, counter, element.susceptible, counter, element.infected)
			#visualization_data+="""data.setValue(%s, 0, new Date(%s, %s ,%s));\ndata.setValue(%s, 1, %s);\ndata.setValue(%s, 4, %s);\n""" % (counter, date.year, date.month-1, date.day, counter, susceptible[date], counter, infected[date])
		except:
			pass

	return visualization_data

def simulation_detail(request, uuid, template_name=None):
	########################################
	# TEMPLATE NAME
	########################################
	if template_name is None:
		template_name = 'simulation_detail.html'
	visualization_data =get_simulation_data(uuid)
	context = {}
	context['visualization_data'] = visualization_data
	return direct_to_template(request, template_name, extra_context=context, context_instance=RequestContext(request))

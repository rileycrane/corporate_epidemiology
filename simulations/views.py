from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.views.generic.simple import direct_to_template


def _get_simulation_data(uuid):
	"""
	Gets daily susceptible and shows those which are > level 1 --> word of mouth
	"""
	try:
		simrun = SimRun.objects.get(uuid=uuid)
	except:
		return HttpResponse("View Does Not Exist")
	
	susceptible = {}
	infected    = {}
	
	# BUILD susceptible DICT: Date, Count
	for sim in simrun:
		if sim.timestamp.date() not in susceptible.keys():
			susceptible[sim.timestamp.date()]=1
		else:
			susceptible[sim.timestamp.date()]+=1
		if sim.level>1:
			if sim.timestamp.date() not in infected.keys():
				infected[sim.timestamp.date()]=1
			else:
				infected[sim.timestamp.date()]+=1

	# Remove None
	try:
		del susceptible[None]
	except KeyError:
		pass
	try:
		del infected[None]
	except KeyError:
		pass
	number_of_rows = len(susceptible.keys()) + len(infected.keys())
	
	visualization_data = """
		data.addColumn('date', 'Date');
		data.addColumn('number', 'Number of Signups');
		data.addColumn('string', 'title1');
		data.addColumn('string', 'text1');
		data.addColumn('number', 'Word of mouth');
		data.addColumn('string', 'title2');
		data.addColumn('string', 'text2');
		
		data.addRows(%s);\n""" % number_of_rows
	
	# BUILD LIST OF ALL DATES:
	all_dates = susceptible.keys() + infected.keys()
	all_dates = uniquify(all_dates)
	all_dates = sorted(all_dates)
	counter = -1
	for date in all_dates:
		counter+=1
		try:
			infected[date]
		except KeyError:
			infected[date]=0
		try:
			susceptible[date]
		except KeyError:
			susceptible[date]=0
		try:
			visualization_data+="""data.setValue(%s, 0, new Date(%s, %s ,%s));\ndata.setValue(%s, 1, %s);\ndata.setValue(%s, 4, %s);\n""" % (counter, date.year, date.month-1, date.day, counter, susceptible[date], counter, infected[date])
		except:
			pass

	return visualization_data

def simulation_detail(request, uuid, template_name=None):
	########################################
	# TEMPLATE NAME
	########################################
	if template_name is None:
		template_name = 'simulation_detail.html'
	visualization_data =_get_simulation_data(uuid)
	context = {}
	context['visualization_data'] = visualization_data
	return direct_to_template(request, template_name, extra_context=context, context_instance=RequestContext(request))

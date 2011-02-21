from django.contrib import admin
from simulations.models import *

class IndividualAdmin(admin.ModelAdmin):
	pass
class InteractionAdmin(admin.ModelAdmin):
	pass
class SimRunAdmin(admin.ModelAdmin):
	date_hierarchy = 'created_at'
	list_display = ('created_at','beta', 'gamma', 'alpha','t_min_filter', 't_max_filter')
	list_filter = ('beta', 'gamma', 'alpha', 't_min_filter', 't_max_filter')

admin.site.register(Individual, IndividualAdmin)
admin.site.register(Interaction, InteractionAdmin)
admin.site.register(SimRun, SimRunAdmin)
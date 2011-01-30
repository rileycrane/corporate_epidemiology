from django.contrib import admin
from simulations.models import *

class IndividualAdmin(admin.ModelAdmin):
	pass
class InteractionAdmin(admin.ModelAdmin):
	pass

admin.site.register(Individual, IndividualAdmin)
admin.site.register(Interaction, InteractionAdmin)
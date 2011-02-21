from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic import list_detail
from simulations.models import SimRun

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

all_simulations = {
	'queryset' : SimRun.objects.all(),
	'template_name': 'simulation_list.html',
}
urlpatterns = patterns('',
	(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	(r'^admin/', include(admin.site.urls)),
	(r'^simulations/$', list_detail.object_list, all_simulations,'simulations'),
	url(r'^simulations/(?P<uuid>[-\w]+)/$', 'simulations.views.simulation_detail'),
)


if settings.DEBUG:
		MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT', './media')
		urlpatterns += patterns('',
				(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
		)

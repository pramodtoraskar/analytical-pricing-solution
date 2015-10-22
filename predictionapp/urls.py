# URls File - All route and respactive views methods.

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'predictionapp.views',
    url(r'^$', 'index', name='Index'),
    url(r'^uploadsd/$', 'upload_seed_data', name='upload_seed_data'),
    url(r'^loadoil/categories/$', 'oil_categories', name='oil_categories'),
    url(r'^render/graph/$', 'render_graph', name='render_graph'),
)
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'futbolmanager.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'futman.views.welcome', name='welcome'),
    url(r'^signup/$', 'futman.views.signup', name='signup'),
    url(r'^logout/$', 'futman.views.logout_view', name='logout'),
    url(r'^home/$', 'futman.views.home', name='home'),
    url(r'^league/$', 'futman.views.league', name='league'),
    url(r'^settings/$', 'futman.views.settings', name='settings'),
    url(r'^join/$', 'futman.views.join', name='join'),
    url(r'^lineup/$', 'futman.views.lineup', name='lineup'),
    url(r'^create_league/$', 'futman.views.create_league', name='create_league'),
    url(r'^create_club/$', 'futman.views.create_club', name='create_club'),
    url(r'^league_settings/$', 'futman.views.league_settings', name='league_settings'),
    url(r'^do_request/$', 'futman.views.send_request_join', name='send_request_join'),

    url(r'^admin/', include(admin.site.urls)),
)

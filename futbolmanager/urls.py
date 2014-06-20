from django.conf.urls import patterns, include, url
from futbolmanager import settings

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
                       url(r'^market/$', 'futman.views.market', name='market'),
                       url(r'^do_request/$', 'futman.views.send_request_join', name='send_request_join'),
                       url(r'^do_bid/$', 'futman.views.dobid', name='do_bid'),
                       url(r'^check_requests/$', 'futman.views.check_join', name='check_requests'),
                       url(r'^accept_offer/$', 'futman.views.accept_offer', name='accept_offer'),
                       url(r'^reject_offer/$', 'futman.views.reject_offer', name='reject_offer'),

                       url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
                            (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                                'document_root': settings.MEDIA_ROOT}))

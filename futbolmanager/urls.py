from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'futbolmanager.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'futman.views.welcome', name='welcome'),
    url(r'^signup/$', 'futman.views.signup', name='signup'),
    url(r'^home/$', 'futman.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
)

from django.conf.urls.defaults import *


urlpatterns = patterns('django_ldap_opus.views',
    url(r'^login/$', 'ldap_login', name='ldap_login_url'),
    url(r'^logout/$', 'logout_view', name='ldap_logout_url'),
    url(r'^test/$', 'ldap_test_page', name='ldap_test_page_url'),
)

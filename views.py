from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from django_ldap_opus.util import get_ldap_roles

from opus.lib import log
log = log.getLogger()


def ldap_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        next = request.POST['next']

        server = settings.SERVER_URL
        
        roles = get_ldap_roles(server, username, password)
        user = authenticate(username=username)
        #roles = str(roles).strip('[').strip(']')
        
        #try:
            #user_profile = user.get_profile()
            #user_profile.ldap_roles = roles
            #user_profile.save()
        #except ObjectDoesNotExist:
            #user_profile = UserProfile(user=user, ldap_roles=roles)
            #user_profile.save()

        if user is not None:
            if roles == None:
                log.debug("Roles were none, redirecting to login")
                return redirect(settings.LOGIN_URL)
            else:
                log.debug("Logging user in")
                login(request, user)
                log.debug("Redirecting to " + next)
                return render_to_response("django_ldap_opus/content.html",
                        context_instance=RequestContext(request))

        else:
            log.debug("No user found")
            return redirect(settings.LOGIN_URL)
    else:
        return render_to_response("django_ldap_opus/login.html",
                context_instance=RequestContext(request))


@login_required
def logout_view(request, template_name=None, redirect_url=None, redirect_viewname=None):
    logout(request)
    
    if not template_name:
        template_name = 'django_ldap_opus/logout.html'

    if "next" in request.GET:
            next = request.GET['next']
    elif not redirect_url:
        if redirect_viewname != None:
            next = reverse(redirect_viewname)
        else:
            next = None
    else:
        next = redirect_url

    return render_to_response(template_name,
            {'next' : next, },
            context_instance=RequestContext(request))

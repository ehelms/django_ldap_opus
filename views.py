from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from django_ldap_opus.util import get_ldap_roles
from django_ldap_opus.models import UserProfile


def ldap_login(request, template_name=None, redirect_viewname=None, redirect_url=None):
    if not template_name:
        template_name = "django_ldap_opus/login.html"
    
    if "next" in request.REQUEST:
            next = request.REQUEST['next']
    elif not redirect_url:
        if redirect_viewname != None:
            next = reverse(redirect_viewname)
        else:
            next = reverse("ldap_test_page_url")
    else:
        next = redirect_url

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        next = request.POST['next']

        server = settings.SERVER_URL
        
        roles, message = get_ldap_roles(server, username, password)
        if not roles:
            return render_to_response(template_name,
                    { 'message' : message, },
                    context_instance=RequestContext(request))

        user = authenticate(username=username)
        
        if settings.USE_LOCAL_LDAP_GROUPS:
            roles = str(roles).strip('[').strip(']')
            try:
                user_profile = user.get_profile()
                user_profile.ldap_roles = roles
                user_profile.save()
            except ObjectDoesNotExist:
                user_profile = UserProfile(user=user, ldap_roles=roles)
                user_profile.save()

        if user is not None:
            login(request, user)
            return redirect(next)
        else:
            return redirect(settings.LOGIN_URL)
    else:
        return render_to_response(template_name,
                { 'next' : next, },
                context_instance=RequestContext(request))


@login_required
def logout_view(request, template_name=None, redirect_url=None, redirect_viewname=None):
    if settings.USE_LOCAL_LDAP_GROUPS:
        user_profile = request.user.get_profile()
        user_profile.delete()
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


@login_required
def ldap_test_page(request):
    return render_to_response("django_ldap_opus/test.html",
            context_instance=RequestContext(request))

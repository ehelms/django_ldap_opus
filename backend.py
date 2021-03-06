from django.contrib.auth.models import User, Permission, Group
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings


class LDAPBackend:
    def authenticate(self, username=None, password=None):
        if not username:
            return None
        else:
            if password == None:
                user, created = User.objects.get_or_create(username=username)
                return user
            else:
                try:
                    user = User.objects.get(username=username)
                    if user.check_password(password):
                        return user
                except User.DoesNotExist:
                    return None


    def get_group_permissions(self, user_obj):
        if settings.USE_LOCAL_LDAP_GROUPS:
            user_obj._perm_cache.update(self.get_ldap_group_permissions(user_obj))
        
        if not hasattr(user_obj, '_group_perm_cache'):
            perms = Permission.objects.filter(group__user=user_obj
                    ).values_list('content_type__app_label', 'codename'
                    ).order_by()
            user_obj._group_perm_cache = set(["%s.%s" % (ct, name) for ct, name in perms])
        return user_obj._group_perm_cache
    
    
    def get_ldap_group_permissions(self, user_obj):
        perms = []
        user_profile = user_obj.get_profile()
        roles = user_profile.ldap_roles
        groups = Group.objects.all()
        for arg in groups:
            group_name = str(arg.name)
            if group_name in roles:
                perms.extend(Permission.objects.filter(group=arg
                ).values_list('content_type__app_label', 'codename').order_by())       
        user_obj._group_perm_cache = set(["%s.%s" % (ct, name) for ct, name in perms])
        return user_obj._group_perm_cache


    def get_all_permissions(self, user_obj):
        if not hasattr(user_obj, '_perm_cache'):
            user_obj._perm_cache = set([u"%s.%s" % (p.content_type.app_label, p.codename) for p in user_obj.user_permissions.select_related()])
            user_obj._perm_cache.update(self.get_group_permissions(user_obj))
        return user_obj._perm_cache

    def has_perm(self, user_obj, perm):
        return perm in self.get_all_permissions(user_obj)

    def has_module_perms(self, user_obj, app_label):
        for perm in self.get_all_permissions(user_obj):
            if perm[:perm.index('.')] == app_label:
                return True
        return False

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


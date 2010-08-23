from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    ldap_roles = models.TextField("User's LDAP Roles", editable=False, blank=True)

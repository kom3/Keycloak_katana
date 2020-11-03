
from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.signals import user_logged_in,user_logged_out
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.

class VZBackupRights(models.Model):
    class Meta:
        managed = False
        permissions = (
            ('readwrite','Read Write'),
            ('usermanagement','User Management'),
            ('downloadbackups','Download Backups'),
            ('readonly','Read Only')
        )

def add_perms_to_vzAdmins(sender, user, request, **kwargs):
  vzusr = User.objects.filter(groups__name='VZ Backup Application Admins')
  for vzadmin in vzusr:
    vzadmin.is_staff = True
    vzadmin.is_superuser = True
    vzadmin.save()
user_logged_in.connect(add_perms_to_vzAdmins)
user_logged_out.connect(add_perms_to_vzAdmins)

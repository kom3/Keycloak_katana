from django.db import migrations
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from ..models import VZBackupRights
from django.contrib.auth.management import create_permissions
from django.contrib.auth import get_user_model
User = get_user_model()

def add_group_permissions(apps, schema_editor):
    # Create Groups for this application
    admin_group, admin_group_created = Group.objects.get_or_create(name='VZ Backup Application Admins')
    user_group, user_group_created = Group.objects.get_or_create(name='VZ Backup  Application Users')
    tech_group, tech_group_created = Group.objects.get_or_create(name='VZ Backup  Application Techs')
    manager_group, manager_group_created = Group.objects.get_or_create(name='VZ Backup  Application Managers')

    # Retrieve permissions for correct model
    content_type = ContentType.objects.get_for_model(VZBackupRights)
    readwrite_perm = Permission.objects.get(content_type=content_type, codename='readwrite')
    usermanagement_perm = Permission.objects.get(content_type=content_type, codename='usermanagement')
    downloadbackup_perm = Permission.objects.get(content_type=content_type, codename='downloadbackups')
    readonly_perm = Permission.objects.get(content_type=content_type, codename='readonly')

    # Assign Permissions to the created Groups
    admin_perms = [
        readwrite_perm,
        usermanagement_perm,
        downloadbackup_perm,
    ]

    #Adding all permissions to Admin Group
    for perm in admin_perms:
        admin_group.permissions.add(perm)

    #Adding readonly permission to User Group
    user_group.permissions.add(readonly_perm)
    user_group.permissions.add(downloadbackup_perm)

    #Adding readwrite and download to permission to Manager Group
    manager_group.permissions.add(readwrite_perm)
    manager_group.permissions.add(downloadbackup_perm)

    #Adding readwrite and download permission to Technician Group
    tech_group.permissions.add(downloadbackup_perm)


def migrate_permissions(apps, schema_editor):
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None
def creatingsuperuser(apps,schema_editor):
   User.objects.create_superuser("admin","admin@example.com","admin123")
class Migration(migrations.Migration):
    dependencies = [
        ('container','0001_initial'),
    ]
    operations = [
        migrations.RunPython(migrate_permissions),
        migrations.RunPython(add_group_permissions),
    ]

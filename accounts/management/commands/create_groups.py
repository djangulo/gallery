# Sets up groups if they don't exist
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission, Group
from django.db.models import Q

class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        superusers, superusers_created = Group.objects.get_or_create(name="Superusers")
        if superusers_created:
            for p in Permission.objects.all():
                superusers.permissions.add(p)
            superusers.save()


        admins, admins_created = Group.objects.get_or_create(name="Admins")
        if admins_created:
            for p in Permission.objects.all().filter(
                    Q(name__icontains='entry') |
                    Q(name__icontains='image') |
                    Q(name__icontains='user')
                ).exclude(
                    Q(name__icontains='log')
                ):
                admins.permissions.add(p)
            admins.save()
            
        staff, staff_created = Group.objects.get_or_create(name="Staff")
        if staff_created:
            for p in Permission.objects.all().filter(
                    Q(name__icontains='entry') |
                    Q(name__icontains='image')
                ).exclude(
                    Q(name__icontains='log') |
                    Q(name__icontains='publish') |
                    Q(name__icontains='delete')
                ):
                staff.permissions.add(p)
            staff.save()

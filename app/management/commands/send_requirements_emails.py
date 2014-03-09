from django.core.management.base import BaseCommand, CommandError
from app import reminder_utilities
import app.models
import pytz
from django.conf import settings
import django.utils.timezone as timezone
import datetime

class Command(BaseCommand):
    args = ''

    def handle(self, *args, **options):
        """
        Sends requirements update emails.
        """
        now = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
        semester = current_semester(now)
        year = now.year
        # get all current, active CKS members
        #people = utilities.active_members(semester=semester, year=year, include_inactive=False, prefetch_related=['tours', 'shifts', 'overridden_requirements'])
        people = [app.models.Person.objects.get(last_name='Raftery')]
        emails_sent = 0
        for person in people:
            reminder_utilities.send_requirements_email(person)
            emails_sent += 1

        self.stdout.write('Sent {} emails successfully.'.format(emails_sent))
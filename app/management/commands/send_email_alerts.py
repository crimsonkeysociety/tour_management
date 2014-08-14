from django.core.management.base import BaseCommand, CommandError
from app.models import Tour, Shift
from app import reminder_utilities
import pytz
from django.conf import settings
import django.utils.timezone as timezone
import datetime

class Command(BaseCommand):
    args = ''
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        """
        Sends text alerts for tours and shifts occurring tomorrow.
        """
        tomorrow = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)) + datetime.timedelta(days=1)

        # get all of tomorrow's tours
        tours = Tour.objects.filter(time__day=tomorrow.day, time__month=tomorrow.month, time__year=tomorrow.year)
        emails_sent = 0
        for tour in tours:
            if tour.guide:
                reminder_utilities.send_email(tour)
                emails_sent += 1

        self.stdout.write(u'Sent {} tour emails successfully.'.format(emails_sent))

        # get all of tomorrow's shifts
        shifts = Shift.objects.filter(time__day=tomorrow.day, time__month=tomorrow.month, time__year=tomorrow.year)
        emails_sent = 0
        for shift in shifts:
            if shift.person:
                reminder_utilities.send_shift_email(shift)
                emails_sent += 1

        self.stdout.write(u'Sent {} shift emails successfully.'.format(emails_sent))
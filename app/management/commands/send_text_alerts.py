from django.core.management.base import BaseCommand, CommandError
from app.models import Tour
from app import reminder_utilities
import pytz
from django.conf import settings
import django.utils.timezone as timezone

class Command(BaseCommand):
    args = ''
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        """
        Sends text alerts for tours occurring today.
        """
        now = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))

        # get all of today's tours
        tours = Tour.objects.filter(time__day=now.day, time__month=now.month, time__year=now.year)
        texts_sent = 0
        for tour in tours:
            if tour.guide:
                reminder_utilities.send_text(tour)
                texts_sent += 1

        self.stdout.write('Sent {} texts successfully.'.format(texts_sent))
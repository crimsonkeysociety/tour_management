from django.core.management.base import BaseCommand, CommandError
from app.models import Tour
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
        Sends text alerts for tours occurring tomorrow.
        """
        reminder_utilities.send_test_email('andrewraftery@gmail.com')
from django.core.management.base import BaseCommand, CommandError
from app.models import Tour
from app import reminder_utilities
import pytz
from django.conf import settings
import django.utils.timezone as timezone
import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
import pytz
from django.conf import settings
from app import models
from twilio.rest import TwilioRestClient
import textwrap

class Command(BaseCommand):
    args = ''
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        plaintext = 'This is a test.'
        htmly     = plaintext
        subject = 'This is a test email.'
        from_email = settings.FROM_EMAIL
        to = 'andrew.raftery@gmail.com'

        text_content = plaintext
        html_content = htmly
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        email_num = 1
        self.stdout.write('Sent {} email to {}.'.format(email_num, to))
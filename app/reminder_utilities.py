from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
import pytz
from django.conf import settings
from app import models
from twilio.rest import TwilioRestClient
import textwrap

def send_text(tour):
	if not tour.guide.phone:
		return False
	account_sid = settings.TWILIO_ACCOUNT_SID
	auth_token  = settings.TWILIO_AUTH_TOKEN
	client = TwilioRestClient(account_sid, auth_token)
	plaintext = get_template('texts/tour_reminder.txt')
	d = Context({ 'tour': tour })
	body = plaintext.render(d)
	bodies = textwrap.wrap(body, 160)
	for body in bodies:
		message = client.sms.messages.create(
		body=body,
    	to="+1{0}".format(tour.guide.phone),
    	from_="+16172998450")


def send_email(tour):
	plaintext = get_template('email/tour_reminder.txt')
	htmly     = get_template('email/tour_reminder.html')
	d = Context({ 'tour': tour })
	subject = 'Tour Tomorrow at {0}'.format(tour.time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%I:%M %p'))
	to = tour.guide.email

	reply_to = models.Person.objects.filter(position='Tour Coordinator (Primary)').first()
	if not reply_to:
		reply_to = models.Person.objects.filter(position='Tour Coordinator').first()

	if reply_to:
		reply_to_email = reply_to.email
	else:
		reply_to_email = 'crimsonkeysociety@gmail.com'

	from_email = reply_to_email

	text_content = plaintext.render(d)
	html_content = htmly.render(d)
	msg = EmailMultiAlternatives(subject, text_content, from_email, [to], headers={'Reply-To': reply_to_email })
	msg.attach_alternative(html_content, "text/html")
	msg.send()
`from django.core.mail import EmailMultiAlternatives
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

def send_requirements_email(person):
	plaintext = get_template('email/requirements_email.txt')
	htmly     = get_template('email/requirements_email.html')

	requirements = person.requirements_status()

	past_tours = requirements['tours']['past_tours']
	upcoming_tours = requirements['tours']['upcoming_tours']

	past_shifts = requirements['shifts']['past_shifts']
	upcoming_shifts = requirements['shifts']['upcoming_shifts']

	tours_required_num = requirements['tours']['tours_required_num']
	completed_tours_num = requirements['tours']['completed_tours_num']

	shift_required_num = requirements['shift']['shift_required_num']
	completed_shift_num = requirements['shift']['completed_shift_num']

	d = Context({ 'person': person, 'past_tours': past_tours, 'upcoming_tours': upcoming_tours, 'past_shifts': past_shifts, 'upcoming_shifts': upcoming_shifts, 'tours_required_num': tours_required_num, 'completed_tours_num': completed_tours_num, 'shift_required_num': shift_required_num, 'completed_shift_num': completed_shift_num })
	subject = 'Requirements Update'
	to = person.email

	reply_to = models.Person.objects.filter(position='Secretary').first()

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

def send_test_email(email):
	text_content = 'Test email'
	html_content     = '<html><body>Test email</body></html>'
	subject = 'Tour Tomorrow at 11'
	to = email

	reply_to_email = 'crimsonkeysociety@gmail.com'

	from_email = reply_to_email

	msg = EmailMultiAlternatives(subject, text_content, from_email, [to], headers={'Reply-To': reply_to_email })
	msg.attach_alternative(html_content, "text/html")
	msg.send()
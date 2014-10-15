from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
import pytz
from django.conf import settings
from django.utils import timezone
from app import models
from twilio.rest import TwilioRestClient
import textwrap
import datetime
from app import utilities
from app import app_settings
from premailer import transform

def send_text(tour):
	if not tour.guide.phone:
		return False
	account_sid = settings.TWILIO_ACCOUNT_SID
	auth_token  = settings.TWILIO_AUTH_TOKEN
	client = TwilioRestClient(account_sid, auth_token)
	plaintext = get_template('texts/tour_reminder.txt')
	d = Context({ 'tour': tour, 'tour_day': tour.time.weekday() })
	body = plaintext.render(d)
	bodies = textwrap.wrap(body, 160)
	for body in bodies:
		message = client.sms.messages.create(
		body=body,
    	to=u"+1{0}".format(tour.guide.phone),
    	from_="+16172998450")

def send_shift_text(shift):
	if not shift.person.phone:
		return False
	account_sid = settings.TWILIO_ACCOUNT_SID
	auth_token  = settings.TWILIO_AUTH_TOKEN
	client = TwilioRestClient(account_sid, auth_token)
	plaintext = get_template('texts/shift_reminder.txt')
	d = Context({ 'shift': shift })
	body = plaintext.render(d)
	bodies = textwrap.wrap(body, 160)
	for body in bodies:
		message = client.sms.messages.create(
		body=body,
    	to=u"+1{0}".format(shift.person.phone),
    	from_="+16172998450")


def send_email(tour):
	plaintext = get_template('email/tour_reminder.txt')
	htmly     = get_template('email/tour_reminder.html')
	subject = u'Tour Tomorrow at {0}'.format(tour.time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%I:%M %p'))
	d = Context({ 'tour': tour, 'tour_day': tour.time.weekday(), 'title': subject })
	to = tour.guide.email

	tour_coordinator_primary = models.Person.objects.filter(position='Tour Coordinator (Primary)').first()
	tour_coordinator2 = models.Person.objects.filter(position='Tour Coordinator').first()

	if tour.source == 'Freshman Week':
		reply_to = models.Person.objects.filter(position='Secretary').first()
	elif tour.source == "Marshall's Office" and tour_coordinator2:
		reply_to = tour_coordinator2
	elif tour_coordinator_primary:
		reply_to = tour_coordinator_primary
	else:
		reply_to = tour_coordinator2

	if not reply_to:
		reply_to_email = 'Crimson Key Society <crimsonkeysociety@gmail.com>'
	else:
		reply_to_email = u'{} <{}>'.format(reply_to.full_name, reply_to.email)

	from_email = reply_to_email

	text_content = plaintext.render(d)
	html_content = transform(htmly.render(d))
	msg = EmailMultiAlternatives(subject, text_content, from_email, [to], headers={'Reply-To': reply_to_email })
	msg.attach_alternative(html_content, "text/html")
	msg.send()

def send_shift_email(shift):
	plaintext = get_template('email/shift_reminder.txt')
	htmly     = get_template('email/shift_reminder.html')
	subject = u'Shift Tomorrow at {0}'.format(shift.time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%I:%M %p'))
	to = shift.person.email
	d = Context({ 'shift': shift, 'title': subject })

	if shift.source == 'Freshman Week':
		reply_to = models.Person.objects.filter(position='Secretary').first()
	elif shift.source == 'TEACH':
		reply_to = models.Person.objects.filter(position='Tour Coordinator').first()

	if not reply_to:
		reply_to_email = 'Crimson Key Society <crimsonkeysociety@gmail.com>'
	else:
		reply_to_email = u'{} <{}>'.format(reply_to.full_name, reply_to.email)

	from_email = reply_to_email

	text_content = plaintext.render(d)
	html_content = transform(htmly.render(d))
	msg = EmailMultiAlternatives(subject, text_content, from_email, [to], headers={'Reply-To': reply_to_email })
	msg.attach_alternative(html_content, "text/html")
	msg.send()

def send_requirements_email(person):
	now = timezone.now()
	semester = utilities.current_semester()
	year = now.year
	plaintext = get_template('email/requirements_email.txt')
	htmly     = get_template('email/requirements_email.html')

	requirements = person.requirements_status()

	past_tours = requirements['tours']['past_tours']
	upcoming_tours = requirements['tours']['upcoming_tours']

	past_shifts = requirements['shifts']['past_shifts']
	upcoming_shifts = requirements['shifts']['upcoming_shifts']

	tours_required_num = requirements['tours']['tours_required_num']
	completed_tours_num = requirements['tours']['completed_tours_num']

	shifts_required_num = requirements['shifts']['shifts_required_num']
	completed_shifts_num = requirements['shifts']['completed_shifts_num']


	semester_end_datetime = datetime.datetime(year, settings.SEMESTER_END[semester][0], settings.SEMESTER_END[semester][1])
	collect_dues_semester = app_settings.COLLECT_DUES(semester_end_datetime)
	if (collect_dues_semester != 'both' and collect_dues_semester != semester):
		collect_dues = False
	else:
		collect_dues = True

	current_semester_kwargs_set = utilities.current_semester_kwargs()
			
	tours = person.tours.filter(**current_semester_kwargs_set).order_by('time')
	person.upcoming_tours = requirements['tours']['upcoming_tours']
	person.upcoming_tours_count = person.upcoming_tours.count()
	person.tour_empties = requirements['tours']['tours_required_remaining'] - person.upcoming_tours_count
	if person.tour_empties < 0:
		person.tour_empties = 0
	person.tour_status = requirements['tours']['status']

	if person.tour_status == 'status_projected':
		completed_num = requirements['tours']['completed_tours_num']
		remaining_num = requirements['tours']['tours_required_remaining']
		person.tour_projected_date = person.upcoming_tours[remaining_num - 1].time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%m/%d/%y')
		person.tour_projected_date = person.tour_projected_date[:2].lstrip('0') + '/' + person.tour_projected_date[3:5].lstrip('0') + '/' + person.tour_projected_date[6:8].lstrip('0')

	elif person.tour_status == 'status_incomplete':
		person.tours_remaining = requirements['tours']['tours_required_remaining'] - person.upcoming_tours_count

	elif person.tour_status == 'status_complete':
		over_requirements = (requirements['tours']['completed_tours_num'] + person.upcoming_tours_count) - requirements['tours']['tours_required_num']
		if over_requirements == 0:
			person.tours_remaining = ''
		else:
			person.tours_remaining = u'+{}'.format(over_requirements)


	# SHIFTS:
	shifts = person.shifts.filter(**current_semester_kwargs_set).order_by('time')
	person.upcoming_shifts = requirements['shifts']['upcoming_shifts']
	person.upcoming_shifts_count = person.upcoming_shifts.count()
	person.shift_empties = requirements['shifts']['shifts_required_remaining'] - person.upcoming_shifts_count
	if person.shift_empties < 0:
		person.shift_empties = 0
	person.shift_status = requirements['shifts']['status']

	if person.shift_status == 'status_projected':
		completed_num = requirements['shifts']['completed_shifts_num']
		remaining_num = requirements['shifts']['shifts_required_remaining']
		person.shift_projected_date = person.upcoming_shifts[remaining_num - 1].time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%m/%d/%y')
		person.shift_projected_date = person.shift_projected_date[:2].lstrip('0') + '/' + person.shift_projected_date[3:5].lstrip('0') + '/' + person.shift_projected_date[6:8].lstrip('0')

	elif person.shift_status == 'status_incomplete':
		person.shifts_remaining = requirements['shifts']['shifts_required_remaining'] - person.upcoming_shifts_count

	elif person.shift_status == 'status_complete':
		over_requirements = (requirements['shifts']['completed_shifts_num'] + person.upcoming_shifts_count) - requirements['shifts']['shifts_required_num']
		if over_requirements == 0:
			person.shifts_remaining = ''
		else:
			person.shifts_remaining = u'+{}'.format(over_requirements)

	# DUES PAYMENTS:
	if collect_dues:
		if person.dues_payments.filter(semester=semester, year=year).count() != 0:
			person.dues_status = 'status_complete'
		else:
			person.dues_status = 'status_incomplete'


	# DETERMINE STATUS
	if person.tour_status == 'status_complete' and person.shift_status == 'status_complete' and (not collect_dues or person.dues_status == 'status_complete'):
		person.status = 'Requirements Complete'
		person.status_class = 'complete'
	elif (person.tour_status == 'status_complete' or person.tour_status == 'status_projected') and (person.shift_status == 'status_complete' or person.shift_status == 'status_projected') and (not collect_dues or person.dues_status == 'status_complete'):
		person.status = 'Projected to Complete'
		person.status_class = 'projected'
	else:
		if person.tour_status == 'status_complete' and person.shift_status == 'status_complete':
			person.status = 'Requirements Incomplete (Dues Unpaid)'
		else:
			person.status = 'Requirements Incomplete'
		person.status_class = 'incomplete'


	reply_to = models.Person.objects.filter(position='Secretary').first()

	if reply_to:
		reply_to_email = reply_to.email
		signature = reply_to.first_name
	else:
		reply_to_email = 'crimsonkeysociety@gmail.com'
		signature = 'CKS'

	from_email = reply_to_email

	d = Context({ 'signature': signature, 'collect_dues': collect_dues, 'person': person, 'past_tours': past_tours, 'upcoming_tours': upcoming_tours, 'past_shifts': past_shifts, 'upcoming_shifts': upcoming_shifts, 'tours_required_num': tours_required_num, 'completed_tours_num': completed_tours_num, 'shifts_required_num': shifts_required_num, 'completed_shifts_num': completed_shifts_num })
	subject = 'Requirements Update'
	to = person.email

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
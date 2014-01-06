from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
import pytz
from django.conf import settings
from app import models

def send_email(tour):
	plaintext = get_template('email/tour_notification.txt')
	htmly     = get_template('email/tour_notification.html')
	d = Context({ 'tour': tour })
	subject = 'Tour Today at {0}'.format(tour.time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%I:%M %p'))
	from_email = settings.FROM_EMAIL
	to = tour.guide.email

	reply_to = models.Person.objects.filter(position='Tour Coordinator (Primary)').first()
	if not reply_to:
		reply_to = models.Person.objects.filter(position='Tour Coordinator').first()

	if reply_to:
		reply_to_email = reply_to.email
	else:
		reply_to_email = 'crimsonkeysociety@gmail.com'

	text_content = plaintext.render(d)
	html_content = htmly.render(d)
	msg = EmailMultiAlternatives(subject, text_content, from_email, [to], headers={'Reply-To': reply_to_email })
	msg.attach_alternative(html_content, "text/html")
	msg.send()
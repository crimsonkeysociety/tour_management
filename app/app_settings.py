from app import models
import django.utils.timezone as timezone
from django.conf import settings
import datetime, pytz


def get_setting(name, time=None):
	if time is None:
		time = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
	try:
		val = models.Setting.objects.filter(name=name, time_set__lte=time).latest('time_set')
	except models.Setting.DoesNotExist:
		# if it doesn't exist for that time, just use the current number
		val = models.Setting.objects.filter(name=name).latest('time_set')

	if val.value_type == 'int':
		return int(val.value)
	elif val.value_type == 'bool':
		return bool(val.value)
	elif val.value_type == 'float':
		return float(val.value)
	else:
		return val.value

# gets tours required per semester
def TOURS_REQUIRED(time=None):
	return get_setting('tours_required', time)

# gets shifts required per semester
def SHIFTS_REQUIRED(time=None):
	return get_setting('shifts_required', time)

def SEND_EMAIL_REMINDERS(time=None):
	return get_setting('send_email_reminders', time)

def SEND_TEXT_REMINDERS(time=None):
	return get_setting('send_text_reminders', time)
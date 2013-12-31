from app import models
import django.utils.timezone as timezone
from django.conf import settings
import datetime, pytz

# gets tours required per semester
def TOURS_REQUIRED(time=None):
	if time is None:
		time = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
	
	try:
		num = models.Setting.objects.filter(name='tours_required', time_set__lte=time).latest('time_set')
	except models.Setting.DoesNotExist:
		# if it doesn't exist for that time, just use the current number
		num = models.Setting.objects.filter(name='tours_required').latest('time_set')

	return int(num.value)

# gets shifts required per semester
def SHIFTS_REQUIRED(time=None):
	if time is None:
		time = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
	try:
		num = models.Setting.objects.filter(name='shifts_required', time_set__lte=time).latest('time_set')
	except models.Setting.DoesNotExist:
		# if it doesn't exist for that time, just use the current number
		num = models.Setting.objects.filter(name='shifts_required').latest('time_set')

	return int(num.value)
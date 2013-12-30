from app import models
import datetime

# gets tours required per semester
def TOURS_REQUIRED(time=None):
	if time is None:
		time = datetime.datetime.now()
	
	num = models.Setting.objects.filter(name='tours_required', time_set__lte=time).latest('time_set')
	
	# if it doesn't exist for that time, just use the current number
	if not num:
		num = models.Setting.objects.filter(name='tours_required').latest('time_set')

	return int(num.value)

# gets shifts required per semester
def SHIFTS_REQUIRED(time=None):
	if time is None:
		time = datetime.datetime.now()
	
	num = models.Setting.objects.filter(name='shifts_required', time_set__lte=time).latest('time_set')
	
	# if it doesn't exist for that time, just use the current number
	if not num:
		num = models.Setting.objects.filter(name='shifts_required').latest('time_set')

	return int(num.value)
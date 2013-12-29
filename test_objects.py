from app import models
import datetime, random, calendar
import pytz

YEAR = 2013
MONTH = 12
TIMES = [(10, 45), (11, 45), (12, 45)]

FROM_ZONE = pytz.timezone('America/New_York')
TO_ZONE = pytz.timezone('UTC')

people = models.Person.objects.all()
weeks = calendar.Calendar().monthdatescalendar(YEAR, MONTH)

for week in weeks:
	for date in week:
		if date.month == MONTH and date.weekday() != 6 and not models.day_canceled(date):
			for time in TIMES:
				time_full_local = datetime.datetime(date.year, date.month, date.day, time[0], time[1])
				time_full_local = time_full_local.replace(tzinfo=FROM_ZONE)
				time_full = time_full_local.astimezone(TO_ZONE)
				tour = models.Tour(guide=people[random.randint(0, len(people)-1)], time=time_full)
				tour.save()
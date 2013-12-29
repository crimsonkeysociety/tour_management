from app import models
import datetime, random, calendar

YEAR = 2013
MONTH = 12

people = models.Person.objects.all()
weeks = calendar.Calendar().monthdatescalendar(YEAR, MONTH)
# (hour, minute)
times = [(10, 45), (11, 45), (12, 45)]

for week in weeks:
	for date in week:
		if date.month == MONTH and not models.day_canceled(date) and day != 6:
			for time in times:
				time_full = datetime.datetime(date.year, date.month, date.day, time[0], time[1])
				person = people[random.randint(0, len(people)-1)]
				tour = models.Tour(time = time_full, guide=person, source="Information Office")
				tour.save()
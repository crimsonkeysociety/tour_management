from app import models
import datetime, calendar, pytz

def day_canceled(day):
    if models.CanceledDay.objects.filter(date=day):
        return True
    else:
        return False

def add_months(sourcedate,months):
	month = sourcedate.month - 1 + months
	year = sourcedate.year + month / 12
	month = month % 12 + 1
	day = min(sourcedate.day,calendar.monthrange(year,month)[1])
	return datetime.date(year,month,day)

def uninitialize_month(month=0, year=0, date=None):
	if month == 0 and year == 0 and date is None:
		raise ValueError
		return
	elif (month == 0 or year == 0) and date is None:
		raise ValueError
		return

	if date is None:
		month = int(month)
		year = int(year)
	else:
		month = date.month
		year = date.year

	month = int(month)
	year = int(year)
	if not is_initialized(month=month, year=year):
		raise ValueError
		return
	tours_to_delete = models.Tour.objects.filter(time__month=int(month), time__year=int(year), default_tour=True)
	tours_to_delete.delete()
	blackouts = models.CanceledDay.objects.filter(date__month=int(month), date__year=int(year))
	blackouts.delete()
	initialized_month = models.InitializedMonth.objects.filter(month=int(month), year=int(year))
	initialized_month.delete()

def add_default_tours(times=[(10,45), (11,45), (12,45)], days=range(0,6)):
	for hour, minute in times:
		for day in days:
			time=datetime.datetime(2000,1,1,hour,minute).replace(tzinfo=pytz.timezone('America/New_York')).astimezone(pytz.timezone('UTC'))
			day_num = day
			tour = models.DefaultTour(time=time, day_num=day_num)
			tour.save()

def is_initialized(month=0, year=0, date=None):
	if month == 0 and year == 0 and date is None:
		raise ValueError
		return
	elif (month == 0 or year == 0) and date is None:
		raise ValueError
		return

	if date is None:
		month = int(month)
		year = int(year)
	else:
		month = date.month
		year = date.year

	if models.InitializedMonth.objects.filter(month=month, year=year):
		return True
	else:
		return False

def weeks_with_tours(month=None, year=None, tours=None):

	try:
		month = int(month)
		year = int(year)
		weeks = calendar.Calendar().monthdays2calendar(year, month)
	# if month or year is not int or are not in range
	except ValueError:
		raise Http404()
		return

	if tours is None:
		tours = models.Tour.objects.filter(time__month=month, time__year=year).order_by('time')

	canceled_days = models.CanceledDay.objects.filter(date__month=month, date__year=year).order_by('date')

	weeks_with_tours = []

	for week_index, week in enumerate(weeks):
		new_week = []
		for date, day in week:
			if date != 0:
				canceled = day_canceled(datetime.datetime(year, month, date))
			else:
				canceled = False
			new_week.append((date, day, tours.filter(time__day=date), canceled))
		weeks_with_tours.append(new_week)

	return weeks_with_tours
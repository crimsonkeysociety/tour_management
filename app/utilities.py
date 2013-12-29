from app import models
import datetime, calendar, pytz, random

def day_canceled(day):
    if models.CanceledDay.objects.filter(date=day):
        return True
    else:
        return False

def add_months(sourcedate,months,return_datetime=False):
	month = sourcedate.month - 1 + months
	year = sourcedate.year + month / 12
	month = month % 12 + 1
	day = min(sourcedate.day,calendar.monthrange(year,month)[1])
	if not return_datetime:
		return datetime.date(year,month,day)
	else:
		return datetime.datetime(year,month,day)

def uninitialize_month(month=None, year=None, date=None):
	month, year = resolve_date(month, year, date)

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

def resolve_date(month, year, date):
	if month is None and year is None and date is None:
		raise ValueError
		return
	elif (month is None or year is None) and date is None:
		raise ValueError
		return

	if date is None:
		month = int(month)
		year = int(year)
	else:
		month = date.month
		year = date.year

	return month, year

def is_initialized(month=None, year=None, date=None):
	month, year = resolve_date(month, year, date)

	if models.InitializedMonth.objects.filter(month=month, year=year):
		return True
	else:
		return False

def weeks_with_tours(month=None, year=None, tours=None, date=None):

	try:
		month, year = resolve_date(month, year, date)
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

def populate_unclaimed_tours(month=None, year=None, date=None):
	month, year = resolve_date(month, year, date)
	unclaimed_tours = models.Tour.objects.filter(time__month=month, time__year=year, guide=None)
	people = models.Person.objects.all()
	for tour in unclaimed_tours:
		person = people[random.randint(0, len(people) - 1)]
		tour.guide = person
		tour.save()
	print '{0} unclaimed tours populated.'.format(len(unclaimed_tours))
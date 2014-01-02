import datetime, calendar, pytz, random, daterange
from django.conf import settings
import models
import django.utils.timezone as timezone
from itertools import chain

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

def current_semester(now=None):
	if now is None:
		now = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))

	now_date = datetime.date(now.year, now.month, now.day)

	fall_start = datetime.date(now.year, settings.FALL_SEMESTER_START[0], settings.FALL_SEMESTER_START[1])
	fall_end = datetime.date(now.year, settings.FALL_SEMESTER_END[0], settings.FALL_SEMESTER_END[1])
	fall_range = list(daterange.daterange(fall_start, fall_end))

	spring_start = datetime.date(now.year, settings.SPRING_SEMESTER_START[0], settings.SPRING_SEMESTER_START[1])
	spring_end = datetime.date(now.year, settings.SPRING_SEMESTER_END[0], settings.SPRING_SEMESTER_END[1])
	spring_range = list(daterange.daterange(spring_start, spring_end))

	if now_date in fall_range:
		return 'fall'
	elif now_date in spring_range:
		return 'spring'
	else:
		return None

def class_years(semester=None, year=None, bookends_only=False):
    if semester is None:
        semester = current_semester()
    if year is None:
        year = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).year
    else:
    	year = int(year)

    if semester == 'fall':
        years = range(year + 1, year + 5)
    elif semester == 'spring':
        years = range(year, year + 4)
    else:
        raise ValueError

    if bookends_only is True:
        return (years[0], years[3])
    else:
        return years

# kwargs for filter() to show members for just the given semester and year (defaults to current)
def current_kwargs(semester=None, year=None):
	if semester is None:
		semester = current_semester()
	if year is None:
		year = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).year
	else:
		year = int(year)

	senior_year, freshman_year = class_years(semester=semester, year=year, bookends_only=True)

	kwargs = {}

	if semester == 'fall':
		kwargs['member_since__lte'] = year
	else:
		kwargs['member_since__lt'] = year
	
	kwargs['year__lte'] = freshman_year
	kwargs['year__gte'] = senior_year

	return kwargs

# kwargs for exclude() to show just active members for the given semester and year (defaults to current)
def exclude_inactive_kwargs(semester=None, year=None):
	if semester is None:
		semester = current_semester()
	if year is None:
		year = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).year
	else:
		year = int(year)

	kwargs = {}
	kwargs['inactive_semesters__year__exact'] = year
	kwargs['inactive_semesters__semester'] = semester

	return kwargs

def merge(*dicts, **kv): 
      return { k:v for d in list(dicts) + [kv] for k,v in d.items() }

def active_members(semester=None, year=None, include_inactive=False):
	if semester is None:
		semester = current_semester()
	if year is None:
		year = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).year
	else:
		year = int(year)

	active_members = models.Person.objects.filter(**(current_kwargs(semester=semester, year=year))).exclude(**(exclude_inactive_kwargs(semester=semester, year=year))).order_by('year', 'last_name', 'first_name')

	# if include_inactive is True, then add members who have not yet graduated but are inaactive for the semester
	# note: if include_inactive is False, return type will be QuerySet, else it will be a list
	if include_inactive is True:
		inactive_members = models.Person.objects.filter(**(current_kwargs(semester=semester, year=year))).filter(**(exclude_inactive_kwargs(semester=semester, year=year))).order_by('year', 'last_name', 'first_name')
		inactive_members_list = []

		# mark these as inactive
		for i in inactive_members:
			i.inactive = True
			inactive_members_list.append(i)

		people = list(chain(active_members, inactive_members_list))
		return people
	else:
		return active_members

# kwargs for filter() to show just tours/shifts from current month
def current_semester_kwargs(semester=None, year=None):
	if semester is None:
		semester = current_semester()
	if year is None:
		year = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).year
	else:
		year = int(year)

	kwargs = {}
	start = datetime.datetime(year, settings.SEMESTER_START[semester][0], settings.SEMESTER_START[semester][1])
	end = datetime.datetime(year, settings.SEMESTER_END[semester][0], settings.SEMESTER_END[semester][1], 23, 59, 59)
	kwargs['time__gte'] = start
	kwargs['time__lte'] = end
	return kwargs

# accepts only 1 or -1 for delta
# returns dictionary in form {'semester': semester, 'year': year} or tuple in form (semester, year)
def delta_semester(semester, year, delta, dictionary=True):
	semesters = ['fall', 'spring']
	if semester not in semesters:
		raise ValueError
	elif delta not in [1, -1]:
		raise ValueError
	try:
		year = int(year)
	except:
		raise ValueError

	new_semester = semesters[(semesters.index(semester) + delta) % 2]
	if semester == 'fall':
		if delta == 1:
			new_year = year + 1
		elif delta == -1:
			new_year = year
	elif semester == 'spring':
		if delta == 1:
			new_year = year
		elif delta == -1:
			new_year = year - 1

	if dictionary is True:
		return {'semester': new_semester, 'year': new_year}
	else:
		return (new_semester, new_year)

def latest_semester(grad_year, member_since):
	semester = current_semester()
	year = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).year
	
	# spring of grad_year
	if semester == 'fall':

		# if has graduated, return spring of their grad year
		if year >= grad_year:
			return ('spring', grad_year)

		# if hasn't graduated
		else:
			if member_since > year:
				return {'semester': semester, 'year': member_since}
			else:
				return {'semester': semester, 'year': year}

	elif semester == 'spring':

		# if has graduated, return spring of their grad year
		if year > grad_year:
			return ('spring', grad_year)

		# if hasn't graduated
		else:
			if member_since >= year:
				return {'semester': semester, 'year': member_since}
			else:
				return {'semester': semester, 'year': year}

	else:
		raise ValueError
		return



def month_initialization_allowed(month, year):
	try:
		month = int(month)
		year = int(year)
	except:
		raise ValueError

	now = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
	date_obj = datetime.datetime(year, month, 1)
	current_month = now.month
	current_year = now.year
	current = datetime.datetime(current_year, current_month, 1)
	last_allowed = add_months(current, 12, True)

	# Make sure this month isn't initialized or out of allowed range
	if (is_initialized(month=month, year=year) or date_obj < current or date_obj > last_allowed):
		return False
	else:
		return True
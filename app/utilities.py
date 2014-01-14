import datetime, calendar, pytz, random, daterange
from django.conf import settings
import models
import django.utils.timezone as timezone
from itertools import chain
from django.core import exceptions
from django.contrib import auth
from django.db.models import Q

def day_canceled(day):
	"""
	Checks if a given day is canceled
	"""

	if models.CanceledDay.objects.filter(date=day):
		return True
	else:
		return False

def add_months(sourcedate,months,return_datetime=False):
	"""
	Takes a source datetime.datetime or datetime.date and adds a number of months.
	Returns a datetime.date by default, but can also returrn a datetime.datetime object.
	"""
	month = sourcedate.month - 1 + months
	year = sourcedate.year + month / 12
	month = month % 12 + 1
	day = min(sourcedate.day,calendar.monthrange(year,month)[1])
	if not return_datetime:
		return datetime.date(year,month,day)
	else:
		return datetime.datetime(year,month,day)

def uninitialize_month(month=None, year=None, date=None):
	"""
	Takes either a month and year, or a datetime.date/datetime.datetime object as input.
	Reverses the month initialization process. Deletes all DefaultTours and CanceledDays
	for a given month. Also deletes the InitializedMonth record.
	"""
	month, year = resolve_date(month, year, date)

	if not is_initialized(month=month, year=year):
		raise ValueError

	tours_to_delete = models.Tour.objects.filter(time__month=int(month), time__year=int(year), default_tour=True)
	tours_to_delete.delete()
	blackouts = models.CanceledDay.objects.filter(date__month=int(month), date__year=int(year))
	blackouts.delete()
	open_months = models.OpenMonth.objects.filter(month=int(month), year=int(year))
	open_months.delete()
	initialized_month = models.InitializedMonth.objects.filter(month=int(month), year=int(year))
	initialized_month.delete()

def add_default_tours(times=[(10,45), (11,45), (12,45)], days=range(0,6)):
	"""
	* DEPRECATED *
	Adds the 10:45, 11:45, and 12:45, Mon-Sat default tours.
	This is just for testing.
	"""
	for hour, minute in times:
		for day in days:
			time=datetime.datetime(2000,1,1,hour,minute).replace(tzinfo=pytz.timezone('America/New_York')).astimezone(pytz.timezone('UTC'))
			day_num = day
			tour = models.DefaultTour(time=time, day_num=day_num)
			tour.save()

def resolve_date(month, year, date):
	"""
	Takes a month and year or datetime object as input. Figures out which
	was given and returns a (month, year) tuple. For use with other utility
	functions.
	>>> resolve_date(2013, 12)
	(2013, 12)
	"""
	if month is None and year is None and date is None:
		raise ValueError
	elif (month is None or year is None) and date is None:
		raise ValueError

	if date is None:
		month = int(month)
		year = int(year)
	else:
		month = date.month
		year = date.year

	return month, year

def is_initialized(month=None, year=None, date=None):
	"""
	Checks if a given month is initialized. Takes a month and year or datetime object as input.
	"""
	month, year = resolve_date(month, year, date)

	if models.InitializedMonth.objects.filter(month=month, year=year):
		return True
	else:
		return False

def weeks_with_tours(month=None, year=None, tours=None, date=None):
	"""
	Returns a list of the weeks of a given month. Each element in each week is a tuple
	in form: (date, day, tours, canceled).
	"""
	try:
		month, year = resolve_date(month, year, date)
		weeks = calendar.Calendar().monthdays2calendar(year, month)
	# if month or year is not int or are not in range
	except ValueError:
		raise Http404()

	if tours is None:
		tours = models.Tour.objects.filter(time__month=month, time__year=year).order_by('time').prefetch_related('guide')

	canceled_days = models.CanceledDay.objects.filter(date__month=month, date__year=year).order_by('date')
	canceled_days_dict = {}
	for day in canceled_days:
		canceled_days_dict[day.date.day] = True

	weeks_with_tours = []

	for week_index, week in enumerate(weeks):
		new_week = []
		for date, day in week:
			if date != 0:
				canceled = canceled_days_dict.get(date, False)
			else:
				canceled = False
			new_week.append((date, day, tours.filter(time__day=date), canceled))
		weeks_with_tours.append(new_week)

	return weeks_with_tours

def populate_unclaimed_tours(month=None, year=None, date=None):
	"""
	* DEPRECATED *
	Fills in unclaimed tours from a given month with random active people.
	This is just for testing.
	"""
	month, year = resolve_date(month, year, date)
	unclaimed_tours = models.Tour.objects.filter(time__month=month, time__year=year, guide=None)
	people = active_members(month=month, year=year)
	for tour in unclaimed_tours:
		person = people[random.randint(0, len(people) - 1)]
		tour.guide = person
		tour.save()
	print '{0} unclaimed tours populated.'.format(len(unclaimed_tours))

def current_semester(now=None):
	"""
	Given a datetime.datetime object, figures out the current semester based on
	the start and end points defined in settings. Returns either 'fall' or 'spring,' or None
	if something goes wrong.
	"""
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
	"""
	Given a semester and year, returns a tuple of the class years currently in school, in ascending order.
	E.g., class_years('fall', 2013) = (2014, 2015, 2016, 2017)
	"""
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
	"""
	Returns kwargs for Person.objects.filter() to select only current members for a given semester.
	This means it does not filter out members marked as inactive for the semester.
	"""
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
	"""
	Returns kwargs for Person.objects.exclude() to exclude members marked as inactive for a given semester.
	"""
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
	"""
	Merges dictionaries. Like [] + [], but for dicts.
	"""
    	return { k:v for d in list(dicts) + [kv] for k,v in d.items() }

def active_members(semester=None, year=None, include_inactive=False, prefetch_related=None):
	"""
	Finds all active members for a given semester and year, using the helper functions current_kwargs()
	and exclude_inactive_kwargs(). Does not use exclude_inactive_kwargs() if include_inactive() is True.
	If include_inactive() is false (default), returns a QuerySet, else returns a list.
	"""
	if semester is None:
		semester = current_semester()
	if year is None:
		year = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).year
	else:
		year = int(year)

	if not prefetch_related:
		prefetch_related = []

	current_kwargs_list = current_kwargs(semester=semester, year=year)
	exclude_inactive_kwargs_list = exclude_inactive_kwargs(semester=semester, year=year)
	active_members = models.Person.objects.filter(**current_kwargs_list).exclude(**exclude_inactive_kwargs_list).order_by('last_name', 'first_name').prefetch_related(*prefetch_related)

	# if include_inactive is True, then add members who have not yet graduated but are inaactive for the semester
	# note: if include_inactive is False, return type will be QuerySet, else it will be a list
	if include_inactive is True:
		inactive_members = models.Person.objects.filter(**current_kwargs_list).filter(**exclude_inactive_kwargs_list).order_by('last_name', 'first_name').prefetch_related(*prefetch_related)
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
	"""
	Returns kwargs for filter to show just tours or shifts for a month.
	Semester/year default to current. For use with Shift.objects.filter() or Tour.objects.filter().
	"""
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
	"""
	Finds the next or previous semester and year, given a semester and year.
	Returns a dictionary in form {'semester': 'fall', 'year: 2013} or tuple in form (semester, year).
	Accepts either 1 or -1 for delta.
	"""
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
	"""
	Finds the latest semester a member was in Crimson Key. For graduated members,
	this means the spring of their senior year. Otherwise, it's usually latest semester
	(as in current_semester()).

	Raises a ValueError if something goes wrong (e.g., a person in the db is not yet a member,
	i.e. member_since > current year).
	"""
	semester = current_semester()
	year = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).year
	
	# spring of grad_year
	if semester == 'fall':

		# if has graduated, return spring of their grad year
		if year >= grad_year:
			return {'semester': 'spring', 'year': grad_year }

		# if hasn't graduated
		else:
			if member_since > year:
				return {'semester': semester, 'year': member_since}
			else:
				return {'semester': semester, 'year': year}

	elif semester == 'spring':

		# if has graduated, return spring of their grad year
		if year > grad_year:
			return {'semester': 'spring', 'semester': grad_year}

		# if hasn't graduated
		else:
			if member_since >= year:
				return {'semester': semester, 'year': member_since}
			else:
				return {'semester': semester, 'year': year}

	else:
		raise ValueError



def month_initialization_allowed(month, year):
	"""
	Checks if a month can be initialized. I.e., checks whether a given month is
	within 12 months of now, and whether it has already been initialzed.
	"""
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


def set_groups_by_position(position, user):
	"""
	Sets permission groups by Board positions, given a user and a position to which they are being
	assigned.
	"""
	position_groups = auth.models.Group.objects.filter(Q(name='President') | Q(name='Vice President') | Q(name='Secretary') | Q(name='Treasurer') | Q(name='Tour Coordinators') | Q(name='Board Members'))
	
	for group in position_groups:
		user.groups.remove(group)

	if position == 'President':
		auth.models.Group.objects.get(name='President').user_set.add(user)
		auth.models.Group.objects.get(name='Board Members').user_set.add(user)
	elif position == 'Vice President':
		auth.models.Group.objects.get(name='Vice President').user_set.add(user)
		auth.models.Group.objects.get(name='Board Members').user_set.add(user)
	elif position == 'Secretary':
		auth.models.Group.objects.get(name='Secretary').user_set.add(user)
		auth.models.Group.objects.get(name='Board Members').user_set.add(user)
	elif position == 'Treasurer':
		auth.models.Group.objects.get(name='Treasurer').user_set.add(user)
		auth.models.Group.objects.get(name='Board Members').user_set.add(user)
	elif position == 'Tour Coordinator' or position == 'Tour Coordinator (Primary)':
		auth.models.Group.objects.get(name='Tour Coordinators').user_set.add(user)
		auth.models.Group.objects.get(name='Board Members').user_set.add(user)
	elif position == 'Other Board Member':
		auth.models.Group.objects.get(name='Board Members').user_set.add(user)


def month_is_open(month, year, return_tuple=False):
	"""
	Checks if a month is 'open' for tour claiming.
	Returns True/False. Optionally returns a tuple that also includes the closing date.
	"""
	now = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
	if models.OpenMonth.objects.filter(month=month, year=year):
		latest = models.OpenMonth.objects.filter(month=month, year=year).latest('id')
		if latest.opens <= now <= latest.closes:
			if return_tuple:
				return True, latest.closes
			else:
				return True
		else:
			if return_tuple:
				return False, None
			else:
				return False
	else:
		if return_tuple:
			return False, None
		else:
			return False

def open_eligible(month, year):
	"""
	Checks whether a month is eligible to be opened. That is, it has not passed yet and is in the current semester.
	"""
	now = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
	month = int(month)
	year = int(year)


	# month is in the current semester, and is the current month or in the future, and the month is initialized
	if month >= now.month and year == now.year and current_semester() == current_semester(datetime.datetime(year, month, 1)) and is_initialized(month=month, year=year):
		return True
	else:
		return False


def is_active(person, year=None, semester=None):
	now = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))

	if semester is None and year is None:
		semester = current_semester()
		year = now.year
	elif semester is None or year is None:
		raise ValueError
	else:
		try:
			year = int(year)
		except:
			raise ValueError

	if person in active_members(semester=semester, year=year):
		return True
	else:
		return False


def user_is_board(user):
	try:
		if user.person.is_board:
			return True
		else:
			return False
	except models.Person.DoesNotExist:
		raise exceptions.PermissionDenied
		return False

def user_is_active(user):
	try:
		if user.person.is_active:
			return True
		else:
			raise exceptions.PermissionDenied
			return False
	except models.Person.DoesNotExist:
		raise exceptions.PermissionDenied
		return False


from django.http import Http404
from django.shortcuts import render, redirect
import calendar, datetime, pytz, hashlib
import django.utils.timezone as timezone
from django.conf import settings
from django.core import urlresolvers, exceptions
from app import app_settings
from app import utilities, models
from app import profiler
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import auth
import social.apps.django_app.default as social_auth
from django.template.loader import render_to_string


@login_required
@user_passes_test(utilities.user_is_active)
def home(request):
	return redirect('public:month-noargs')


@login_required
@user_passes_test(utilities.user_is_active)
def month(request, year=None, month=None):
	now = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
	
	if year is None and month is None:
		year = now.year
		month = now. month
	elif (year is None and month is not None) or (year is not None and month is None):
		raise Http404()
	else:
		try:
			year = int(year)
			month = int(month)
		except:
			raise Http404()
	
	weeks_with_tours = utilities.weeks_with_tours(month=month, year=year)

	now = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))

	next_month = utilities.add_months(datetime.date(year, month, 1), 1)
	prev_month = utilities.add_months(datetime.date(year, month, 1), -1)

	if models.InitializedMonth.objects.filter(month=month, year=year):
		month_initialized = True
	else:
		month_initialized = False

	months_list = [(num, name) for num, name in enumerate(list(calendar.month_name)) if num != 0]

	is_open, date_closes = utilities.month_is_open(month=month, year=year, return_tuple=True)

	try:
		primary_tour_coordinator = models.Person.objects.filter(position='Tour Coordinator (Primary)').first()
	except:
		primary_tour_coordinator = None

	return render(request, 'public/month.html', { 'months_list': months_list, 'weeks': weeks_with_tours, 'now': now, 'month': month, 'year': year, 'next_year': (year + 1), 'prev_year': (year - 1), 'next_month': next_month, 'prev_month': prev_month, 'month_initialized': month_initialized, 'is_open': is_open, 'date_closes': date_closes, 'primary_tour_coordinator': primary_tour_coordinator})

@login_required
@user_passes_test(utilities.user_is_active)
def profile(request, year=None, semester=None):
	now = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
	
	if semester is None and year is None:
		semester = utilities.current_semester()
		year = now.year
	elif semester is None or year is None:
		raise Http404()
	else:
		try:
			year = int(year)
		except:
			raise Http404()

	# make sure this semester is not in the future
	current_semester = utilities.current_semester()
	if current_semester == 'spring':
		if semester == 'spring':
			if year > now.year:
				raise Http404()
		elif semester == 'fall':
			if year >= now.year:
				raise Http404()
	elif current_semester == 'fall':
		if year > now.year:
			raise Http404()

	try:
		person = models.Person.objects.filter(id=request.user.person.id).prefetch_related('tours', 'shifts', 'overridden_requirements').first()
	except:
		raise Http404()

	if not utilities.is_active(person=person, semester=semester, year=year):
		raise Http404()

	prev_semester = utilities.delta_semester(semester=semester, year=year, delta=-1)
	if not utilities.is_active(person=person, semester=prev_semester['semester'], year=prev_semester['year']):
		prev_semester = None

	next_semester = utilities.delta_semester(semester=semester, year=year, delta=1)
	if not utilities.is_active(person=person, semester=next_semester['semester'], year=next_semester['year']):
		next_semester = None

	if current_semester == semester and year == now.year:
		next_semester = None

	semester_end_datetime = datetime.datetime(year, settings.SEMESTER_END[semester][0], settings.SEMESTER_END[semester][1])
	collect_dues_semester = app_settings.COLLECT_DUES(semester_end_datetime)
	if (collect_dues_semester != 'both' and collect_dues_semester != semester):
		collect_dues = False
	else:
		collect_dues = True

	current_semester_kwargs_set = utilities.current_semester_kwargs(semester=semester, year=year)
	
	requirements = person.requirements_status(semester=semester, year=year, current_semester_kwargs_set=current_semester_kwargs_set)
			
	tours = person.tours.filter(**current_semester_kwargs_set).order_by('time')
	person.upcoming_tours = requirements['tours']['upcoming_tours']
	person.upcoming_tours_count = person.upcoming_tours.count()
	person.tour_empties = requirements['tours']['tours_required_remaining'] - person.upcoming_tours_count
	if person.tour_empties < 0:
		person.tour_empties = 0
	person.tour_status = requirements['tours']['status']

	if person.tour_status == 'status_projected':
		completed_num = requirements['tours']['completed_tours_num']
		remaining_num = requirements['tours']['tours_required_remaining']
		person.tour_projected_date = person.upcoming_tours[remaining_num - 1].time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%m/%d/%y')
		person.tour_projected_date = person.tour_projected_date[:2].lstrip('0') + '/' + person.tour_projected_date[3:5].lstrip('0') + '/' + person.tour_projected_date[6:8].lstrip('0')

	elif person.tour_status == 'status_incomplete':
		person.tours_remaining = requirements['tours']['tours_required_remaining'] - person.upcoming_tours_count

	elif person.tour_status == 'status_complete':
		over_requirements = (requirements['tours']['completed_tours_num'] + person.upcoming_tours_count) - requirements['tours']['tours_required_num']
		if over_requirements == 0:
			person.tours_remaining = ''
		else:
			person.tours_remaining = u'+{}'.format(over_requirements)


	# SHIFTS:
	shifts = person.shifts.filter(**current_semester_kwargs_set).order_by('time')
	person.upcoming_shifts = requirements['shifts']['upcoming_shifts']
	person.upcoming_shifts_count = person.upcoming_shifts.count()
	person.shift_empties = requirements['shifts']['shifts_required_remaining'] - person.upcoming_shifts_count
	if person.shift_empties < 0:
		person.shift_empties = 0
	person.shift_status = requirements['shifts']['status']

	if person.shift_status == 'status_projected':
		completed_num = requirements['shifts']['completed_shifts_num']
		remaining_num = requirements['shifts']['shifts_required_remaining']
		person.shift_projected_date = person.upcoming_shifts[remaining_num - 1].time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%m/%d/%y')
		person.shift_projected_date = person.shift_projected_date[:2].lstrip('0') + '/' + person.shift_projected_date[3:5].lstrip('0') + '/' + person.shift_projected_date[6:8].lstrip('0')

	elif person.shift_status == 'status_incomplete':
		person.shifts_remaining = requirements['shifts']['shifts_required_remaining'] - person.upcoming_shifts_count

	elif person.shift_status == 'status_complete':
		over_requirements = (requirements['shifts']['completed_shifts_num'] + person.upcoming_shifts_count) - requirements['shifts']['shifts_required_num']
		if over_requirements == 0:
			person.shifts_remaining = ''
		else:
			person.shifts_remaining = u'+{}'.format(over_requirements)

	# DUES PAYMENTS:
	if collect_dues:
		if person.dues_payments.filter(semester=semester, year=year).count() != 0:
			person.dues_status = 'status_complete'
		else:
			person.dues_status = 'status_incomplete'


	# DETERMINE STATUS
	if person.tour_status == 'status_complete' and person.shift_status == 'status_complete' and (not collect_dues or person.dues_status == 'status_complete'):
		person.status = 'Requirements Complete'
		person.status_class = 'complete'
	elif (person.tour_status == 'status_complete' or person.tour_status == 'status_projected') and (person.shift_status == 'status_complete' or person.shift_status == 'status_projected') and (not collect_dues or person.dues_status == 'status_complete'):
		person.status = 'Projected to Complete'
		person.status_class = 'projected'
	else:
		if person.tour_status == 'status_complete' and person.shift_status == 'status_complete':
			person.status = 'Requirements Incomplete (Dues Unpaid)'
		else:
			person.status = 'Requirements Incomplete'
		person.status_class = 'incomplete'

	return render(request, 'public/profile.html', {'person': person, 'semester': semester, 'year': year, 'tours': tours, 'shifts': shifts, 'next_semester': next_semester, 'prev_semester': prev_semester, 'collect_dues': collect_dues})


@login_required
@user_passes_test(utilities.user_is_active)
def claim(request, id, confirm=None):
	try:
		tour = models.Tour.objects.get(id=id)
	except:
		raise Http404()

	if tour.guide is not None or not tour.claim_eligible:
		raise Http404()

	confirm_val = hashlib.md5(str(tour.id)).hexdigest()[:10]

	if confirm == confirm_val:
		tour.guide = request.user.person
		tour.save()
		return redirect('public:month', month=tour.time.month, year=tour.time.year)

	return render(request, 'public/claim.html', {'tour': tour, 'confirm_val': confirm_val})


@login_required
@user_passes_test(utilities.user_is_active)
def unclaim(request, id, confirm=None):
	try:
		tour = models.Tour.objects.get(id=id)
	except:
		raise Http404()

	if tour.guide != request.user.person or not utilities.month_is_open(year=tour.time.year, month=tour.time.month):
		raise Http404()

	confirm_val = hashlib.md5(str(tour.id)).hexdigest()[:10]

	if confirm == confirm_val:
		tour.guide = None
		tour.save()
		return redirect('public:month', month=tour.time.month, year=tour.time.year)

	return render(request, 'public/unclaim.html', {'tour': tour, 'confirm_val': confirm_val})



@login_required
@user_passes_test(utilities.user_is_active)
def help(request):
	try:
		tour_coordinator = models.Person.objects.filter(position='Tour Coordinator (Primary)').first()
	except:
		tour_coordinator = None


	try:
		secretary = models.Person.objects.filter(position='Secretary').first()
	except:
		secretary = None

	markdown = render_to_string('public/documentation.md', { 'tour_coordinator': tour_coordinator, 'secretary': secretary })
	return render(request, 'public/help.html', { 'markdown': markdown })


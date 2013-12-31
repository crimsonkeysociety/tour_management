from django.http import Http404
from django.shortcuts import render, redirect
from app import models, forms, utilities
import calendar, datetime, pytz
import django.utils.timezone as timezone
from django.forms.models import model_to_dict
from django.conf import settings
from django.core import urlresolvers
from collections import Counter
from django.forms import formsets
from app import app_settings
import pprint
# Create your views here.

def cal(request):
    weeks = calendar.Calendar().monthdays2calendar(2013, 12)
    return render(request, 'calendar.html', {'weeks': weeks})

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

	return render(request, 'month.html', { 'weeks': weeks_with_tours, 'now': now, 'month': month, 'year': year, 'next_month': next_month, 'prev_month': prev_month})

def tour(request, id):
	tour = models.Tour.objects.get(id=id)
	if request.method == 'POST':
		form = forms.TourForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			models.Tour.objects.filter(id=id).update(**data)
			return redirect('month-url', month=data['time'].month, year=data['time'].year)
		else:
			# TODO: ERRORS
			raise Http404(form.errors, form.cleaned_data, form.data)
			return
	else:
		tour.time = tour.time.astimezone(pytz.timezone(settings.TIME_ZONE))
		form_initial = model_to_dict(tour)
		form = forms.TourForm(initial=form_initial)
	return render(request, 'tour.html', {'form': form, 'tour': tour})

def initialize_month(request, year=None, month=None):
	# if the year and month need to be chosen, show the choose form or process it if it's being submitted
	if year is None and month is None:
		# if the choose month form is being submitted, process it
		date = request.GET.get('date', None)
		try:
			date_obj = datetime.datetime.strptime(date, '%m/%Y')
			year = date_obj.year
			month = date_obj.month
		except:
			pass

		if year is not None and month is not None:
			now = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
			current_month = now.month
			current_year = now.year
			current = datetime.datetime(current_year, current_month, 1)
			last_allowed = utilities.add_months(current, 12, True)

			if date_obj <= last_allowed and date_obj >= current:
				return redirect('initialize-month-url', month=month, year=year)

		# if form wasn't sent or wasn't valid
		now = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
		months = [utilities.add_months(now, i) for i in range(0, 13)]
		months_choices = []
		for month in months:
			if not utilities.is_initialized(date=month):
				months_choices.append((month.strftime('%m/%Y'), month.strftime('%B %Y')))
		return render(request, 'initialize_month.html', {'choices': months_choices})
	else:
		if request.method == 'POST':
			try:
				month = int(month)
				year = int(year)
				
				if utilities.is_initialized(month=month, year=year):
					raise ValueError

				selected_days = request.POST['selected_days']

				if selected_days != '':
					selected_days_counter = Counter([int(i) for i in selected_days.split(',')])
				else:
					selected_days_counter = Counter()

				month_dates_counter = Counter([i for i in calendar.Calendar().itermonthdays(year, month) if i != 0])
				result_counter = month_dates_counter - selected_days_counter

				for num, times in result_counter.items():
					for i in range(times):
						date = datetime.date(year, month, num)
						canceled_day = models.CanceledDay(date=date)
						canceled_day.save()

				# add default tours on non-blacked out days
				canceled_days = models.CanceledDay.objects.filter(date__month=month)
				default_tours = models.DefaultTour.objects.all()
				weeks = calendar.Calendar().monthdatescalendar(year, month)
				for week in weeks:
					for date in week:
						if date.month == month and not utilities.day_canceled(date):
							for tour in default_tours.filter(day_num=date.weekday):
								add_tour = models.Tour(source=tour.source, time=datetime.datetime(date.year, date.month, date.day, tour.time.hour, tour.time.minute).replace(tzinfo=pytz.timezone('UTC')), notes=tour.notes, length=tour.length, default_tour=True)
								add_tour.save()

				# mark month as initialized
				initialized_month = models.InitializedMonth(month=month, year=year)
				initialized_month.save()

				return redirect('edit-month-url', month=month, year=year)
			except:
				raise Http404()
		else:
			# TODO: check to make sure this month is within the next 12, and that it hasn't yet been initialized
			try:
				now = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
				month = int(month)
				year = int(year)
				date_obj = datetime.datetime(year, month, 1)
				current_month = now.month
				current_year = now.year
				current = datetime.datetime(current_year, current_month, 1)
				last_allowed = utilities.add_months(current, 12, True)
				
				if utilities.is_initialized(month=month, year=year) or date_obj < current or date_obj > last_allowed:
					raise ValueError
			except:
				raise Http404()

			weeks = calendar.Calendar().monthdays2calendar(year, month)
			return render(request, 'initialize_month_picker.html', { 'weeks': weeks, 'month': month, 'year': year })

def edit_month(request, month=None, year=None):
	if request.method == 'POST':
		try:
			month = int(month)
			year = int(year)
		except:
			raise Http404()
			return

		formset = forms.MonthFormSet(request.POST)
		if formset.is_valid():
			data = formset.cleaned_data
			for tour in data:
				existing = models.Tour.objects.filter(id=tour['tour_id']).update(guide=tour['guide'])
			return redirect('month-url', month=month, year=year)
		else:
			return redirect('edit-month-url', month=month, year=year)

	else:	
		try:
			month = int(month)
			year = int(year)
		except:
			raise Http404()

		tours = models.Tour.objects.filter(time__month=month, time__year=year) 
		formset_initial = []
		for tour in tours:
			formset_initial.append({
				'guide': tour.guide,
				'tour_id': tour.id
				})
		formset = forms.MonthFormSet(initial=formset_initial)
		forms_by_id = {}
		for form in formset:
			forms_by_id[str(form.initial['tour_id'])] = form

		weeks = utilities.weeks_with_tours(month=month, year=year, tours=tours)

		return render(request, 'edit-month.html', { 'weeks': weeks, 'month': month, 'year': year, 'formset': formset, 'forms_by_id': forms_by_id })

def roster(request, semester=None, year=None):
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

	prev_semester = utilities.delta_semester(semester=semester, year=year, delta=-1)
	next_semester = utilities.delta_semester(semester=semester, year=year, delta=1)

	# roster
	people = utilities.active_members(semester=semester, year=year)
	tours_required_num = app_settings.TOURS_REQUIRED(datetime.datetime(year, settings.SEMESTER_END[semester][0], settings.SEMESTER_END[semester][1]))
	shifts_required_num = app_settings.SHIFTS_REQUIRED(datetime.datetime(year, settings.SEMESTER_END[semester][0], settings.SEMESTER_END[semester][1]))

	# requirements
	for person in people:
		# TOURS:
		completed_and_upcoming_tours_num = person.tours.filter(**(utilities.current_semester_kwargs(semester=semester, year=year))).filter(missed=False).count()
		person.past_tours = person.tours.filter(**(utilities.current_semester_kwargs(semester=semester, year=year))).filter(time__lte=now).order_by('time')
		person.upcoming_tours = person.tours.filter(**(utilities.current_semester_kwargs(semester=semester, year=year))).filter(time__gt=now).order_by('time')

		if completed_and_upcoming_tours_num < tours_required_num:
			person.tour_empties = tours_required_num - completed_and_upcoming_tours_num
		else:
			person.tour_empties = 0

		if (completed_and_upcoming_tours_num - person.upcoming_tours.count()) >= tours_required_num:
			person.tour_status = 'status_complete'
		elif completed_and_upcoming_tours_num >= tours_required_num:
			person.tour_status = 'status_projected'
			completed_num = completed_and_upcoming_tours_num - person.upcoming_tours.count()
			remaining_num = tours_required_num - completed_num
			person.tour_projected_date = person.upcoming_tours[remaining_num - 1].time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%m/%d/%y')
			person.tour_projected_date = person.tour_projected_date[:2].lstrip('0') + '/' + person.tour_projected_date[3:5].lstrip('0') + '/' + person.tour_projected_date[6:8].lstrip('0')

		else:
			person.tour_status = 'status_incomplete'
			person.tours_remaining = tours_required_num - completed_and_upcoming_tours_num


		# SHIFTS:
		completed_and_upcoming_shifts_num = person.shifts.filter(**(utilities.current_semester_kwargs(semester=semester, year=year))).filter(missed=False).count()
		person.past_shifts = person.shifts.filter(**(utilities.current_semester_kwargs(semester=semester, year=year))).filter(time__lte=now).order_by('time')
		person.upcoming_shifts = person.shifts.filter(**(utilities.current_semester_kwargs(semester=semester, year=year))).filter(time__gt=now).order_by('time')

		if completed_and_upcoming_shifts_num < shifts_required_num:
			person.shift_empties = shifts_required_num - completed_and_upcoming_shifts_num
		else:
			person.shift_empties = 0

		if (completed_and_upcoming_shifts_num - person.upcoming_shifts.count()) >= shifts_required_num:
			person.shift_status = 'status_complete'
		elif completed_and_upcoming_shifts_num >= shifts_required_num:
			person.shift_status = 'status_projected'
			completed_num = completed_and_upcoming_shifts_num - person.upcoming_shifts.count()
			remaining_num = shifts_required_num - completed_num
			person.shift_projected_date = person.upcoming_shifts[remaining_num - 1].time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%m/%d/%y')
			person.shift_projected_date = person.shift_projected_date[:2].lstrip('0') + '/' + person.shift_projected_date[3:5].lstrip('0') + '/' + person.shift_projected_date[6:8].lstrip('0')
		else:
			person.shift_status = 'status_incomplete'
			person.shifts_remaining = shifts_required_num - completed_and_upcoming_shifts_num

	return render(request, 'roster.html', {'people':people, 'semester': semester, 'year': year, 'prev_semester': prev_semester, 'next_semester': next_semester})

def shift(request, id):
	shift = models.Shift.objects.get(id=id)
	if request.method == 'POST':
		form = forms.ShiftForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			models.Shift.objects.filter(id=id).update(**data)
			return redirect('roster-url', semester=utilities.current_semester(data['time']), year=data['time'].year)
		else:
			# TODO: ERRORS
			raise Http404(form.errors, form.cleaned_data, form.data)
			return
	else:
		shift.time = shift.time.astimezone(pytz.timezone(settings.TIME_ZONE))
		form_initial = model_to_dict(shift)
		form = forms.ShiftForm(initial=form_initial)
	return render(request, 'shift.html', {'form': form, 'shift': shift})
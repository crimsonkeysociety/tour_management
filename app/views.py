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
import pprint
# Create your views here.

def cal(request):
    weeks = calendar.Calendar().monthdays2calendar(2013, 12)
    return render(request, 'calendar.html', {'weeks': weeks})

def month(request, year=datetime.datetime.now().year, month=datetime.datetime.now().month):
	try:
		year = int(year)
		month = int(month)
	except:
		raise Http404()
	
	weeks_with_tours = utilities.weeks_with_tours(month=month, year=year)

	now = timezone.now()

	next_month = utilities.add_months(datetime.date(year, month, 1), 1)
	prev_month = utilities.add_months(datetime.date(year, month, 1), -1)

	return render(request, 'month.html', { 'weeks': weeks_with_tours, 'now': now, 'month': month, 'year': year, 'next_month': next_month, 'prev_month': prev_month})

def tour(request, id):
	tour = models.Tour.objects.get(id=id)
	if request.method == 'POST':
		form = forms.TourForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			#time = time.replace(tzinfo=pytz.timezone('America/New_York')).astimezone(pytz.timezone('UTC'))
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
			current_month = datetime.datetime.now().month
			current_year = datetime.datetime.now().year
			current = datetime.datetime(current_year, current_month, 1)
			last_allowed = utilities.add_months(current, 12, True)

			if date_obj <= last_allowed and date_obj >= current:
				return redirect('initialize-month-url', month=month, year=year)

		# if form wasn't sent or wasn't valid
		now = datetime.datetime.now()
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
				month = int(month)
				year = int(year)
				date_obj = datetime.datetime(year, month, 1)
				current_month = datetime.datetime.now().month
				current_year = datetime.datetime.now().year
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

def roster(request):
	people = models.Person.objects.filter(active=True).order_by('year', 'last_name', 'first_name')
	return render(request, 'roster.html', {'people':people})
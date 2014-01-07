from django.http import Http404
from django.shortcuts import render, redirect
from app import models, forms, utilities
import calendar, datetime, pytz
import django.utils.timezone as timezone
from django.forms.models import model_to_dict
from django.conf import settings
from django.core import urlresolvers, exceptions
from collections import Counter
from django.forms import formsets
from app import app_settings
from app import profiler
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import auth
import social.apps.django_app.default as social_auth
# Create your views here.

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
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

	return render(request, 'month.html', { 'months_list': months_list, 'weeks': weeks_with_tours, 'now': now, 'month': month, 'year': year, 'next_year': (year + 1), 'prev_year': (year - 1), 'next_month': next_month, 'prev_month': prev_month, 'month_initialized': month_initialized})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
@permission_required('app.change_tour')
def tour(request, id):
	try:
		tour = models.Tour.objects.get(id=id)
	except:
		raise Http404()

	if request.method == 'POST':
		form = forms.TourForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			models.Tour.objects.filter(id=id).update(**data)
			return redirect('month-url', month=data['time'].month, year=data['time'].year)
	else:
		tour.time = tour.time.astimezone(pytz.timezone(settings.TIME_ZONE))
		form_initial = model_to_dict(tour)
		form = forms.TourForm(initial=form_initial)
	return render(request, 'tour.html', {'form': form, 'tour': tour})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
@permission_required('app.add_tour')
def new_tour(request):
	if request.method == 'POST':
		form = forms.TourForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			models.Tour.objects.create(**data)
			return redirect('month-url', month=data['time'].month, year=data['time'].year)
		else:
			pass
	else:
		now = timezone.now()
		delta = datetime.timedelta(1)
		time = (datetime.datetime(now.year, now.month, now.day, 12) + delta).replace(tzinfo=pytz.timezone('America/New_York'))
		form = forms.TourForm(initial={'time':time})
	return render(request, 'tour.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
@permission_required('app.delete_tour')
def delete_tour(request, id, confirm=None):
	try:
		tour = models.Tour.objects.get(id=id)
	except:
		raise Http404()

	if confirm is not None:
		try:
			confirm = int(confirm)
		except:
			raise Http404()

	if tour.default_tour is False:
		tour.delete()
		return redirect('month-url', month=tour.time.month, year=tour.time.year)
	elif confirm is None:
		return render(request, 'tour_delete_confirm.html', {'tour': tour, 'confirm_value': (tour.id ** 2)})
	elif confirm == (tour.id ** 2):
		tour.delete()
		return redirect('month-url', month=tour.time.month, year=tour.time.year)
	else:
		raise Http404()

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
@permission_required('app.add_initializedmonth')
@permission_required('app.add_canceledday')
def initialize_month(request, year=None, month=None):
	# if the year and month need to be chosen, show the choose form or process it if it's being submitted
	if year is None and month is None:
		# if the choose form was submitted:
		date = request.GET.get('date', None)
		if date is not None:
			date = datetime.datetime.strptime(date, '%m/%Y')
			return redirect('initialize-month-url', month=date.month, year=date.year)
		else:
			# send the form
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

				# Make sure this month isn't initialized or out of allowed range
				if not utilities.month_initialization_allowed(month=month, year=year):
					raise ValueError

				selected_days = request.POST.get('selected_days', None)
				
				if selected_days is None:
					raise ValueError

				if selected_days != '':
					selected_days_counter = Counter([int(i) for i in selected_days.split(',')])
				else:
					selected_days_counter = Counter()

				month_dates_counter = Counter([i for i in calendar.Calendar().itermonthdays(year, month) if i != 0])
				result_counter = month_dates_counter - selected_days_counter

				for num, times in result_counter.items():
					date = datetime.date(year, month, num)
					canceled_day = models.CanceledDay(date=date)
					canceled_day.save()

				# add default tours on non-blacked out days
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

				# Make sure this month isn't initialized or out of allowed range
				if not utilities.month_initialization_allowed(month=month, year=year):
					raise ValueError
			except:
				raise Http404()

			weeks = calendar.Calendar().monthdays2calendar(year, month)
			return render(request, 'initialize_month_picker.html', { 'weeks': weeks, 'month': month, 'year': year })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
@permission_required('app.change_tour')
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

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
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
	people = utilities.active_members(semester=semester, year=year, include_inactive=True, prefetch_related=['tours', 'shifts', 'overridden_requirements'])
	
	if request.method == 'GET':
		tours_required_num = app_settings.TOURS_REQUIRED(datetime.datetime(year, settings.SEMESTER_END[semester][0], settings.SEMESTER_END[semester][1]))
		shifts_required_num = app_settings.SHIFTS_REQUIRED(datetime.datetime(year, settings.SEMESTER_END[semester][0], settings.SEMESTER_END[semester][1]))
		current_semester_kwargs = utilities.current_semester_kwargs(semester=semester, year=year)
		# requirements
		for person in people:
			if person.overridden_requirements:
				special_requirements = person.overridden_requirements.filter(year=year, semester=semester)
			else:
				special_requirements = None

			if special_requirements:
				tours_required_num_user = special_requirements[0].tours_required
				shifts_required_num_user = special_requirements[0].shifts_required
			else:
				tours_required_num_user = tours_required_num
				shifts_required_num_user = shifts_required_num

			# TOURS:
			completed_and_upcoming_tours_num = person.tours.filter(**current_semester_kwargs).filter(missed=False).count()
			person.past_tours = person.tours.filter(**current_semester_kwargs).filter(time__lte=now).order_by('time')
			person.upcoming_tours = person.tours.filter(**current_semester_kwargs).filter(time__gt=now).order_by('time')

			if completed_and_upcoming_tours_num < tours_required_num_user:
				person.tour_empties = tours_required_num_user - completed_and_upcoming_tours_num
			else:
				person.tour_empties = 0

			if (completed_and_upcoming_tours_num - person.upcoming_tours.count()) >= tours_required_num_user:
				person.tour_status = 'status_complete'
			elif completed_and_upcoming_tours_num >= tours_required_num_user:
				person.tour_status = 'status_projected'
				completed_num = completed_and_upcoming_tours_num - person.upcoming_tours.count()
				remaining_num = tours_required_num_user - completed_num
				person.tour_projected_date = person.upcoming_tours[remaining_num - 1].time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%m/%d/%y')
				person.tour_projected_date = person.tour_projected_date[:2].lstrip('0') + '/' + person.tour_projected_date[3:5].lstrip('0') + '/' + person.tour_projected_date[6:8].lstrip('0')

			else:
				person.tour_status = 'status_incomplete'
				person.tours_remaining = tours_required_num_user - completed_and_upcoming_tours_num


			# SHIFTS:
			completed_and_upcoming_shifts_num = person.shifts.filter(**current_semester_kwargs).filter(missed=False).count()
			person.past_shifts = person.shifts.filter(**current_semester_kwargs).filter(time__lte=now).order_by('time')
			person.upcoming_shifts = person.shifts.filter(**current_semester_kwargs).filter(time__gt=now).order_by('time')

			if completed_and_upcoming_shifts_num < shifts_required_num_user:
				person.shift_empties = shifts_required_num_user - completed_and_upcoming_shifts_num
			else:
				person.shift_empties = 0

			if (completed_and_upcoming_shifts_num - person.upcoming_shifts.count()) >= shifts_required_num_user:
				person.shift_status = 'status_complete'
			elif completed_and_upcoming_shifts_num >= shifts_required_num_user:
				person.shift_status = 'status_projected'
				completed_num = completed_and_upcoming_shifts_num - person.upcoming_shifts.count()
				remaining_num = shifts_required_num_user - completed_num
				person.shift_projected_date = person.upcoming_shifts[remaining_num - 1].time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%m/%d/%y')
				person.shift_projected_date = person.shift_projected_date[:2].lstrip('0') + '/' + person.shift_projected_date[3:5].lstrip('0') + '/' + person.shift_projected_date[6:8].lstrip('0')
			else:
				person.shift_status = 'status_incomplete'
				person.shifts_remaining = shifts_required_num_user - completed_and_upcoming_shifts_num

			# DUES PAYMENTS:
			if person.dues_payments.filter(semester=semester, year=year).count() != 0:
				person.dues_payment_form = forms.DuesPaymentForm(initial={'person_id': person.id, 'paid': True}, prefix='id_' + str(person.id))
				person.dues_status = 'status_complete'
			else:
				person.dues_payment_form = forms.DuesPaymentForm(initial={'person_id': person.id, 'paid': False}, prefix='id_' + str(person.id))
				person.dues_status = 'status_incomplete'

		return render(request, 'roster.html', {'people':people, 'semester': semester, 'year': year, 'prev_semester': prev_semester, 'next_semester': next_semester})
	else:
		if not request.user.has_perm('app.add_duespayment') or not request.user.has_perm('app.delete_duespayment') or not request.user.has_perm('app.change_duespayment'):
			raise exceptions.PermissionDenied

		to_be_saved = []
		for person in people:
			form = forms.DuesPaymentForm(request.POST, prefix='id_' + str(person.id))
			data = form.data
			paid = data.get('id_' + str(person.id) + '-paid', False)
			current_dues_payments = person.dues_payments.filter(semester=semester, year=year)
			
			if current_dues_payments and paid is False:
				current_dues_payments.delete()
			elif not current_dues_payments and paid == 'on':
				to_be_saved.append(models.DuesPayment(person=person, semester=semester, year=year))

		if to_be_saved:
			models.DuesPayment.objects.bulk_create(to_be_saved)

		return redirect('roster-url', semester=semester, year=year)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
@permission_required('app.change_shift')
def shift(request, id):
	try:
		shift = models.Shift.objects.get(id=id)
	except:
		raise Http404()

	if request.method == 'POST':
		form = forms.ShiftForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			models.Shift.objects.filter(id=id).update(**data)
			return redirect('roster-url', semester=utilities.current_semester(data['time']), year=data['time'].year)
	else:
		shift.time = shift.time.astimezone(pytz.timezone(settings.TIME_ZONE))
		form_initial = model_to_dict(shift)
		form = forms.ShiftForm(initial=form_initial)
	return render(request, 'shift.html', {'form': form, 'shift': shift})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
@permission_required('app.delete_shift')
def delete_shift(request, id):
	try:
		shift = models.Shift.objects.get(id=id)
	except:
		raise Http404()
	shift.delete()
	return redirect('roster-url', semester=utilities.current_semester(shift.time), year=shift.time.year)

def new_shift(request):
	if request.method == 'POST':
		form = forms.ShiftForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			models.Shift.objects.create(**data)
			return redirect('roster-url', semester=utilities.current_semester(data['time']), year=data['time'].year)
	else:
		now = timezone.now()
		delta = datetime.timedelta(1)
		time = (datetime.datetime(now.year, now.month, now.day, 12) + delta).replace(tzinfo=pytz.timezone('America/New_York'))
		form = forms.ShiftForm(initial={'time':time})
	return render(request, 'shift.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
@permission_required('app.change_person')
@permission_required('app.add_inactivesemester')
@permission_required('app.change_inactivesemester')
@permission_required('app.delete_inactivesemester')
def person(request, id):
	try:
		person = models.Person.objects.get(id=id)
		person_old = models.Person.objects.get(id=id)
	except:
		raise Http404()
	
	semester = utilities.current_semester()
	year = timezone.now().year

	if request.method == 'POST':
		
		i = 0
		semester_forms = []
		while request.POST.get('num_' + str(i) + '_semester', False):
			semester_forms.append({ 'semester': request.POST.get('num_' + str(i) + '_semester', None), 'year': request.POST.get('num_' + str(i) + '_year', None) })
			i += 1

		for semester_form in semester_forms:
			semester_year = int(semester_form['year'])
			if semester_form['semester'] in ['fall', 'spring']:
				if not person.inactive_semesters.filter(semester=semester_form['semester'], year=semester_year):
					models.InactiveSemester(semester=semester_form['semester'], year=semester_year, person=person).save()

		special_requirements_tours = request.POST.get('tours_required', None)
		special_requirements_shifts = request.POST.get('shifts_required', None)
		if special_requirements_tours is not None:
			try:
				special_requirements_tours = int(special_requirements_tours.strip())
			except:
				special_requirements_tours = None

		if special_requirements_shifts is not None:
			try:
				special_requirements_shifts = int(special_requirements_shifts.strip())
			except:
				special_requirements_shifts = None

		if special_requirements_tours is not None or special_requirements_shifts is not None:
			# get default if none
			if special_requirements_tours is None:
				special_requirements_tours = app_settings.TOURS_REQUIRED(timezone.now())
			
			if special_requirements_shifts is None:
				special_requirements_shifts = app_settings.SHIFTS_REQUIRED(timezone.now())

			current_special_requirements = person.overridden_requirements.filter(year=year, semester=semester).first()
			if current_special_requirements:
				current_special_requirements.tours_required = special_requirements_tours
				current_special_requirements.shifts_required = special_requirements_shifts
				current_special_requirements.save()
			else:
				models.OverrideRequirement(year=year, semester=semester, person=person, tours_required=special_requirements_tours, shifts_required=special_requirements_shifts).save()

		form = forms.PersonForm(request.POST, instance=person)
		if form.is_valid():
			data = form.cleaned_data
			if not request.user.person.site_admin or request.user.person == person:
				del data['site_admin']
				person.site_admin = person_old.site_admin

			site_admin = data.get('site_admin', None)
			position = data.get('position', None)
			harvard_email = data.get('harvard_email', None)
			first_name = data.get('first_name', None)
			last_name = data.get('last_name', None)
			
			# if first_name changed
			if first_name != person_old.first_name:
				person.user.first_name = first_name
				person.user.save()

			# if last_name changed
			if last_name != person_old.last_name:
				person.user.last_name = last_name
				person.user.save()
			
			# if site_admin status has changed
			if site_admin is not None and site_admin != person_old.site_admin:
				person.user.is_staff = site_admin
				person.user.is_superuser = site_admin
				person.user.save()

			# if position status has changed, update groups
			if position is not None and position != person_old.position:
				utilities.set_groups_by_position(position=position, user=person.user)

			# if harvard_email has changed, update user
			if harvard_email is not None and person_old.harvard_email != harvard_email:
				person.user.email = harvard_email
				person.user.username = harvard_email.split('@')[0]
				person.user.save()
				user_social_auth = social_auth.models.UserSocialAuth.objects.get(user=person.user)
				user_social_auth.uid = harvard_email
				user_social_auth.save()

			person.save()
			models.Person.objects.filter(id=id).update(**data)
			return_to = utilities.latest_semester(grad_year=data['year'], member_since=data['member_since'])
			return redirect('roster-url', semester=return_to['semester'], year=return_to['year'])
	else:
		form = forms.PersonForm(instance=person)

	special_requirements = person.overridden_requirements.filter(year=year, semester=semester).first()

	return render(request, 'person.html', {'form': form, 'person': person, 'semester': semester, 'special_requirements': special_requirements, 'year': year, 'inactive_semesters_all': person.inactive_semesters.all()})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
@permission_required('app.delete_person')
def delete_person(request, id, confirm=None):
	try:
		person = models.Person.objects.get(id=id)
		if confirm is not None:
			confirm = int(confirm)
	except:
		raise Http404()

	return_to = utilities.latest_semester(grad_year=person.year, member_since=person.member_since)

	if confirm is None:
		tours = person.tours.all()
		shifts = person.shifts.all()
		return render(request, 'person_delete_confirm.html', {'person': person, 'confirm_value': (person.id ** 2), 'return_to': return_to, 'tours': tours, 'shifts': shifts})
	elif confirm == (person.id ** 2):
		u = person.user
		person.delete()
		# will cascade and delete social-auth objects too
		u.delete()
		return redirect('roster-url', semester=return_to['semester'], year=return_to['year'])
	else:
		raise Http404()

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
@permission_required('app.add_person')
def new_person(request):
	if request.method == 'POST':
		form = forms.PersonForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			if not request.user.person.site_admin:
				del data['site_admin']
			models.Person.objects.create(**data)

			harvard_email = data['harvard_email']
			username = harvard_email.split('@college.harvard.edu')[0]
			auth.models.User.objects.create_user(username=username, email=harvard_email, first_name=data['first_name'], last_name=data['last_name'])
			created_person = models.Person.objects.get(harvard_email=harvard_email)
			created_user = auth.models.User.objects.get(email=harvard_email)
			created_person.user = created_user
			created_person.save()
			social_auth.models.UserSocialAuth(user=created_user, provider='google', uid=harvard_email).save()

			site_admin = data.get('site_admin', False)
			position = data['position']

			utilities.set_groups_by_position(position=position, user=created_user)

			if site_admin == True:
				created_user.is_staff = True
				created_user.is_superuser = True
				created_user.save()

			return_to = utilities.latest_semester(grad_year=data['year'], member_since=data['member_since'])
			return redirect('roster-url', semester=return_to['semester'], year=return_to['year'])
	else:
		form = forms.PersonForm()
	return render(request, 'person.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
@permission_required('app.delete_inactivesemester')
def delete_inactive_semester(request, id):
	try:
		inactive_semester = models.InactiveSemester.objects.get(id=id)
	except:
		raise Http404()

	person = inactive_semester.person
	inactive_semester.delete()

	return redirect('person-url', id=person.id)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
@permission_required('app.add_initializedmonth')
@permission_required('app.change_initializedmonth')
@permission_required('app.delete_initializedmonth')
@permission_required('app.change_canceledday')
@permission_required('app.add_canceledday')
@permission_required('app.delete_canceledday')
def edit_month_initialization(request, year, month):
	if request.method == 'POST':
		try:
			month = int(month)
			year = int(year)

			# Make sure this month is initialized
			if not models.InitializedMonth.objects.filter(month=month, year=year):
				raise ValueError

			canceled_days = models.CanceledDay.objects.filter(date__month=month, date__year=year)

			selected_days = request.POST['selected_days']

			if selected_days != '':
				selected_days_counter = Counter([int(i) for i in selected_days.split(',')])
			else:
				selected_days_counter = Counter()

			month_dates_counter = Counter([i for i in calendar.Calendar().itermonthdays(year, month) if i != 0])
			canceled_days_counter = Counter([int(i.date.day) for i in canceled_days])
			marked_days_counter = (month_dates_counter - selected_days_counter)
			turn_back_on_counter = canceled_days_counter - marked_days_counter
			turn_off_counter = marked_days_counter - canceled_days_counter

			for num, times in turn_off_counter.items():
				date = datetime.date(year, month, num)
				canceled_day = models.CanceledDay(date=date)
				canceled_day.save()

				# delete existing default tours on this day
				models.Tour.objects.filter(time__month=month, time__year=year, time__day=num, default_tour=True).delete()
			
			default_tours = models.DefaultTour.objects.all()
			for num, times in turn_back_on_counter.items():
				date = datetime.date(year, month, num)
				models.CanceledDay.objects.filter(date=date).delete()

				# add default tours
				for tour in default_tours.filter(day_num=date.weekday):
					add_tour = models.Tour(source=tour.source, time=datetime.datetime(date.year, date.month, date.day, tour.time.hour, tour.time.minute).replace(tzinfo=pytz.timezone('UTC')), notes=tour.notes, length=tour.length, default_tour=True)
					add_tour.save()

			return redirect('month-url', month=month, year=year)
		except:
			raise Http404()
	else:
		# TODO: check to make sure this month is within the next 12, and that it hasn't yet been initialized
		try:
			month = int(month)
			year = int(year)

			# Make sure this month is initialized
			if not models.InitializedMonth.objects.filter(month=month, year=year):
				raise ValueError
		except:
			raise Http404()

		weeks_with_tours = utilities.weeks_with_tours(month=month, year=year)

		return render(request, 'edit_month_initialization.html', { 'weeks': weeks_with_tours, 'month': month, 'year': year })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
@permission_required('app.delete_initializedmonth')
@permission_required('app.delete_canceledday')
def uninitialize_month(request, year, month, confirm=None):
	try:
		year = int(year)
		month = int(month)
	except:
		raise Http404()

	if confirm is None:
		return render(request, 'month_uninitialize_confirm.html', {'year': year, 'month': month, 'confirm_value': (year * month)})
	else:
		try:
			confirm = int(confirm)
			if confirm == (year * month):
				utilities.uninitialize_month(year=year, month=month)
				return redirect('month-url', month=month, year=year)
		except:
			raise Http404()

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
def settings_page(request):
	existing_settings = models.Setting.objects.raw('SELECT DISTINCT app_setting.id, app_setting.order_num FROM app_setting INNER JOIN (SELECT MAX(id) AS id FROM app_setting GROUP BY name) maxid ON app_setting.id = maxid.id ORDER BY app_setting.order_num ASC')
	
	if request.method == 'POST':
		if not request.user.has_perm('app.add_setting') or not request.user.has_perm('app.change_setting'):
			raise exceptions.PermissionDenied
		
		formset = forms.SettingFormSet(request.POST)
		if formset.is_valid():
			data = formset.cleaned_data
			for setting in data:
				time = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
				try:
					existing_setting = models.Setting.objects.filter(name=setting['name'], time_set__lte=time).latest('time_set')
					if existing_setting.value != setting['value']:
						models.Setting(name=existing_setting.name, description=existing_setting.description, order_num=existing_setting.order_num, value_type=existing_setting.value_type, time_set=time, value=setting['value']).save()
				except models.Setting.DoesNotExist:
					# if it doesn't exist for that time
					raise ValueError

			return redirect('settings-url')
		else:
			forms_by_name = {}
			for form in formset:
				forms_by_name[str(form.instance.name)] = form

	else:
		formset_initial = []
		for setting in existing_settings:
			formset_initial.append({
				'name': setting.name,
				'value': setting.value,
				})
		formset = forms.SettingFormSet(initial=formset_initial)

		forms_by_name = {}
		for form in formset:
			forms_by_name[str(form.initial['name'])] = form

		default_tours = models.DefaultTour.objects.all().order_by('day_num', 'time')

	return render(request, 'settings.html', {'forms_by_name': forms_by_name, 'settings': existing_settings, 'formset': formset, 'default_tours': default_tours})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
@permission_required('app.change_defaulttour')
def default_tour(request, id):
	try:
		tour = models.DefaultTour.objects.get(id=id)
	except:
		raise Http404()

	if request.method == 'POST':
		form = forms.DefaultTourForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			models.DefaultTour.objects.filter(id=id).update(**data)
			return redirect('settings-url')
	else:
		form = forms.DefaultTourForm(instance=tour)
	return render(request, 'default_tour.html', {'form': form, 'tour': tour})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
@permission_required('app.new_defaulttour')
def new_default_tour(request):
	if request.method == 'POST':
		form = forms.DefaultTourForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			models.DefaultTour(**data).save()
			return redirect('settings-url')
	else:
		form = forms.DefaultTourForm()
	return render(request, 'default_tour.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Board Members').count() != 0)
@permission_required('app.delete_defaulttour')
def delete_default_tour(request, id):
	try:
		tour = models.DefaultTour.objects.get(id=id)
	except:
		raise Http404()

	tour.delete()
	return redirect('settings-url')


@login_required
def home(request):
	if request.user.groups.filter(name='Board Members').count() == 0:
		raise exceptions.PermissionDenied
	else:
		return redirect('month-url-noargs')


def login(request):
    """Login view, displays login mechanism"""
    if request.user.is_authenticated():
        return redirect('home-url')
    return render(request, 'social_auth/login.html')


def logout(request):
    """Logs out user"""
    auth.logout(request)
    return redirect('home-url')


from django import forms
from app import models, utilities
import datetime, pytz, re
from django.conf import settings
from django.forms import formsets
import django.core.exceptions as exceptions
from django.db.models import Q
import django.utils.timezone as timezone
from django.core import validators
import calendar

class TourForm(forms.Form):
	utcnow = datetime.datetime.utcnow()
	utcnow = utcnow.replace(tzinfo=pytz.utc)
	tznow = utcnow.astimezone(pytz.timezone(settings.TIME_ZONE))
	offset = tznow.strftime('%z')
	time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'datepicker formcontrol'}, format="%m/%d/%Y %I:%M %p"), input_formats=["%m/%d/%Y %I:%M %p"])
	notes = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'rows': 3, 'placeholder':'These notes will be sent to the tour guide in the tour reminder email. Include location or other special instructions here.' }),required=False)
	guide = forms.ModelChoiceField(queryset=models.Person.objects.filter(**(utilities.current_kwargs())).exclude(**(utilities.exclude_inactive_kwargs())).order_by('last_name', 'first_name'), empty_label='Unclaimed', required=False)
	source = forms.ChoiceField(choices=models.Tour.source_choices, required=False)
	missed = forms.BooleanField(required=False)
	late = forms.BooleanField(required=False)
	length = forms.IntegerField(max_value=999, required=False) # Tour length, in minutes


	def clean_guide(self):
		guide = self.cleaned_data.get('guide', None)
		time = self.cleaned_data.get('time', None)
		if guide is None or time is None:
			return guide
		semester = utilities.current_semester(time)
		if not models.Person.objects.filter(**(utilities.current_kwargs(semester=semester, year=time.year))).filter(id=guide.id):
			if time > timezone.now():
				verb = 'will not be'
			else:
				verb = 'was not'
			raise exceptions.ValidationError(('This member {0} be active at the time of this tour.'.format(verb)), code='invalid')
		else:
			return guide

	def __init__(self, *args, **kwargs):
		super(TourForm, self).__init__(*args, **kwargs)
		current_time = kwargs.get('current_time', None)
		if not current_time:
			initial = kwargs.get('initial', None)
			if initial and initial['time']:
				current_time = initial['time']

		if not current_time:
			current_time = timezone.now()

		current_semester = utilities.current_semester(current_time)
		self.fields['guide'].queryset = models.Person.objects.filter(**(utilities.current_kwargs(semester=current_semester, year=current_time.year))).exclude(**(utilities.exclude_inactive_kwargs(semester=current_semester, year=current_time.year))).order_by('last_name', 'first_name')



class ShiftForm(forms.Form):
	utcnow = datetime.datetime.utcnow()
	utcnow = utcnow.replace(tzinfo=pytz.utc)
	tznow = utcnow.astimezone(pytz.timezone(settings.TIME_ZONE))
	offset = tznow.strftime('%z')
	time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'datepicker formcontrol'}, format="%m/%d/%Y %I:%M %p"), input_formats=["%m/%d/%Y %I:%M %p"])
	notes = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'rows': 3}), required=False)
	person = forms.ModelChoiceField(queryset=models.Person.objects.filter(**(utilities.current_kwargs())).exclude(**(utilities.exclude_inactive_kwargs())).order_by('last_name', 'first_name'), empty_label='--Select a Person--', required=True)
	source = forms.ChoiceField(choices=models.Shift.source_choices, required=False)
	missed = forms.BooleanField(required=False)
	late = forms.BooleanField(required=False)
	length = forms.IntegerField(max_value=999, required=False) # Tour length, in minutes

class DuesPaymentForm(forms.Form):
	person_id = forms.IntegerField(widget=forms.HiddenInput)
	paid = forms.BooleanField()

class MonthForm(forms.Form):
	guide = forms.ModelChoiceField(queryset=models.Person.objects.filter(**(utilities.current_kwargs())).exclude(**(utilities.exclude_inactive_kwargs())).order_by('last_name', 'first_name'), empty_label='Unclaimed', required=False)
	tour_id = forms.IntegerField(widget=forms.HiddenInput, required=True)


	def clean_guide(self):
		guide = self.cleaned_data.get('guide', None)
		time = self.cleaned_data.get('time', None)
		if guide is None or time is None:
			return guide
		semester = utilities.current_semester(time)
		if not models.Person.objects.filter(**(utilities.current_kwargs(semester=semester, year=time.year))).filter(id=guide.id):
			if time > timezone.now():
				verb = 'will not be'
			else:
				verb = 'was not'
			raise exceptions.ValidationError(('This member {0} be active at the time of this tour.'.format(verb)), code='invalid')
		else:
			return guide
	
	def __init__(self, *args, **kwargs):
		super(MonthForm, self).__init__(*args, **kwargs)
		current_time = kwargs.get('current_time', None)
		if not current_time:
			initial = kwargs.get('initial', None)
			if initial and initial['time']:
				current_time = initial['time']

		if not current_time:
			current_time = timezone.now()

		current_semester = utilities.current_semester(current_time)
		self.fields['guide'].queryset = models.Person.objects.filter(**(utilities.current_kwargs(semester=current_semester, year=current_time.year))).exclude(**(utilities.exclude_inactive_kwargs(semester=current_semester, year=current_time.year))).order_by('last_name', 'first_name')


class DefaultTourForm(forms.ModelForm):
	day_choices = [(i, day) for i, day in enumerate(calendar.day_name)]

	time = forms.DateTimeField(widget=forms.TimeInput(attrs={'class': 'timepicker formcontrol'}, format="%I:%M %p"), input_formats=["%I:%M %p"])
	notes = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'rows': 3, 'placeholder':'These notes will be sent to the tour guide in the tour reminder email. Include location or other special instructions here.' }),required=False)
	day_num = forms.ChoiceField(choices=day_choices, label="Day")
	source = forms.ChoiceField(choices=models.Tour.source_choices, required=False)

	class Meta:
		model = models.DefaultTour
		fields = ('time', 'day_num', 'notes', 'source', 'length',)
		
class PersonForm(forms.ModelForm):
	class Meta:
		model = models.Person
		fields = ('first_name', 'last_name', 'email', 'harvard_email', 'phone', 'year', 'member_since', 'position', 'site_admin', 'house', 'notes',)
		labels = {
			'email': 'Primary Email',
			'year': 'Graduation Year',
			'member_since': 'Member of CKS Since Year:'
		}

	def clean_harvard_email(self):
		harvard_email = self.cleaned_data.get('harvard_email', None)
		if harvard_email is not None:
			harvard_email = harvard_email.lower()

		# make sure no existing users have this address
		if harvard_email is not None and harvard_email != '' and self.instance.pk is None:
			if models.Person.objects.filter(Q(email=harvard_email) | Q(harvard_email=harvard_email)):
				raise exceptions.ValidationError(('A member with this email address already exists.'), code='invalid')

		# make sure it's a valid harvard address
		try:
			if harvard_email.split('@')[1] != 'college.harvard.edu':
				raise exceptions.ValidationError(('Please enter a valid @college email address.'), code='invalid')
			else:
				return harvard_email
		except IndexError:
			raise exceptions.ValidationError(('Please enter a valid @college email address.'), code='invalid')


	def clean_phone(self):
		phone = self.cleaned_data['phone']
		if phone != '' and len(phone) < 10:
			raise exceptions.ValidationError(('Phone number is not 10 digits long.'), code='invalid')
		elif phone == '':
			return phone
		else:
			phone = re.sub(r'\D', '', phone)

			if phone[0] == '1':
				phone = phone[1:]

			if len(phone) != 10:
				raise exceptions.ValidationError(('Phone number is not 10 digits long.'), code='invalid')

		if models.Person.objects.filter(phone=phone) and self.instance.pk is None:
			raise exceptions.ValidationError(('A member with this phone number already exists.'), code='invalid')

		return phone

	def clean_first_name(self):
		first_name = self.cleaned_data['first_name']
		return first_name.capitalize()

	def clean_last_name(self):
		last_name = self.cleaned_data['last_name']
		return last_name.capitalize()

	def clean_email(self):
		email = self.cleaned_data.get('email', None)
		if email is not None and email != '' and self.instance.pk is None:
			if models.Person.objects.filter(Q(email=email) | Q(harvard_email=email)):
				raise exceptions.ValidationError(('A member with this email address already exists.'), code='invalid')

		return email

	def clean(self):
		year = self.cleaned_data.get('year', None)
		member_since = self.cleaned_data.get('member_since', None)
		site_admin = self.cleaned_data.get('site_admin', None)
		position = self.cleaned_data.get('position', None)

		if year is not None and member_since is not None and year <= member_since:
			raise exceptions.ValidationError(('Member since graduation year must be greater than member since year.'), code='invalid')
		
		if site_admin is True and position == 'Regular Member':
			raise exceptions.ValidationError(('Only board members can be site admins.'), code='invalid')

		return self.cleaned_data



MonthFormSet = formsets.formset_factory(MonthForm, extra=0)

class SettingForm(forms.ModelForm):
	class Meta:
		model = models.Setting
		fields = ('name', 'value',)
	name = forms.CharField(widget=forms.HiddenInput)

	def clean_value(self):
		name = self.cleaned_data['name']
		value = self.cleaned_data['value']
		now = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
		existing_setting = models.Setting.objects.filter(name=name, time_set__lte=now).latest('time_set')
		value_type = existing_setting.value_type
		
		# validate based on value_type
		if value_type == 'int':
			validators.validate_integer(value)
		elif value_type == 'string':
			try:
				str(value)
			except:
				raise exceptions.ValidationError(('Please enter a valid string.'), code='invalid')
		elif value_type == 'float':
			try:
				float(value)
			except:
				raise exceptions.ValidationError(('Please enter a valid float.'), code='invalid')
		elif value_type == 'email':
			validators.validate_email(value)
		elif value_type == 'bool':
			try:
				if int(value) not in [0, 1]:
					raise exceptions.ValidationError(('Please enter either 0 or 1.'), code='invalid')
			except:
				raise exceptions.ValidationError(('Please enter either 0 or 1.'), code='invalid')
				
			validators.validate_integer(value)

		return self.cleaned_data['value']



SettingFormSet = formsets.formset_factory(SettingForm, extra=0)
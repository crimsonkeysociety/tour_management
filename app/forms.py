from django import forms
from app import models, utilities
import datetime, pytz, re
from django.conf import settings
from django.forms import formsets
import django.core.exceptions as exceptions

class TourForm(forms.Form):
	utcnow = datetime.datetime.utcnow()
	utcnow = utcnow.replace(tzinfo=pytz.utc)
	tznow = utcnow.astimezone(pytz.timezone(settings.TIME_ZONE))
	offset = tznow.strftime('%z')
	time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'datepicker formcontrol'}, format="%m/%d/%Y %I:%M %p"), input_formats=["%m/%d/%Y %I:%M %p"])
	notes = forms.CharField(max_length=2000, widget=forms.Textarea, required=False)
	guide = forms.ModelChoiceField(queryset=models.Person.objects.filter(**(utilities.current_kwargs())).exclude(**(utilities.exclude_inactive_kwargs())).order_by('last_name', 'first_name'), empty_label='Unclaimed', required=False)
	source = forms.ChoiceField(choices=models.Tour.source_choices, required=False)
	missed = forms.BooleanField(required=False)
	late = forms.BooleanField(required=False)
	length = forms.IntegerField(max_value=999, required=False) # Tour length, in minutes

class ShiftForm(forms.Form):
	utcnow = datetime.datetime.utcnow()
	utcnow = utcnow.replace(tzinfo=pytz.utc)
	tznow = utcnow.astimezone(pytz.timezone(settings.TIME_ZONE))
	offset = tznow.strftime('%z')
	time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'datepicker formcontrol'}, format="%m/%d/%Y %I:%M %p"), input_formats=["%m/%d/%Y %I:%M %p"])
	notes = forms.CharField(max_length=2000, widget=forms.Textarea, required=False)
	person = forms.ModelChoiceField(queryset=models.Person.objects.filter(**(utilities.current_kwargs())).exclude(**(utilities.exclude_inactive_kwargs())).order_by('last_name', 'first_name'), empty_label='--Select a Person--', required=True)
	source = forms.ChoiceField(choices=models.Shift.source_choices, required=False)
	missed = forms.BooleanField(required=False)
	late = forms.BooleanField(required=False)
	length = forms.IntegerField(max_value=999, required=False) # Tour length, in minutes

class MonthForm(forms.Form):
	guide = forms.ModelChoiceField(queryset=models.Person.objects.filter(**(utilities.current_kwargs())).exclude(**(utilities.exclude_inactive_kwargs())).order_by('last_name', 'first_name'), empty_label='Unclaimed', required=False)
	tour_id = forms.IntegerField(widget=forms.HiddenInput, required=True)

class PersonForm(forms.ModelForm):
	class Meta:
		model = models.Person
		fields = ('first_name', 'last_name', 'email', 'secondary_email', 'phone', 'year', 'member_since', 'house', 'person_permissions', 'notes',)
		labels = {
			'email': 'Primary Email',
			'year': 'Graduation Year',
			'member_since': 'Member of CKS Since Year:',
			'person_permissions': 'Site Permissions'
		}

	def clean_phone(self):
		phone = self.cleaned_data['phone']
		if phone != '' and len(phone) < 10:
			raise exceptions.ValidationError('Phone number is not 10 digits long.')
		elif phone == '':
			return phone
		else:

			phone = re.sub(r'\D', '', phone)

			if phone[0] == '1':
				phone = phone[1:]

			if len(phone) != 10:
				raise exceptions.ValidationError('Phone number is not 10 digits long.')

		return phone

	def clean_first_name(self):
		first_name = self.cleaned_data['first_name']
		return first_name.capitalize()

	def clean_last_name(self):
		last_name = self.cleaned_data['last_name']
		return last_name.capitalize()

	def clean(self):
		if self.cleaned_data['year'] < self.cleaned_data['member_since']:
			raise exceptions.ValidationError('Member since year cannot be after graduation year.')
		
		return self.cleaned_data

MonthFormSet = formsets.formset_factory(MonthForm, extra=0)
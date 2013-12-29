from django import forms
from app import models, utilities
import datetime, pytz
from django.conf import settings
from django.forms import formsets

class TourForm(forms.Form):
	utcnow = datetime.datetime.utcnow()
	utcnow = utcnow.replace(tzinfo=pytz.utc)
	tznow = utcnow.astimezone(pytz.timezone(settings.TIME_ZONE))
	offset = tznow.strftime('%z')
	time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'datepicker formcontrol'}, format="%m/%d/%Y %I:%M %p " + offset))
	notes = forms.CharField(max_length=2000, widget=forms.Textarea)
	guide = forms.ModelChoiceField(queryset=models.Person.objects.all().order_by('last_name'), empty_label='Unclaimed')
	source = forms.ChoiceField(choices=models.Tour.source_choices)
	missed = forms.BooleanField()
	late = forms.BooleanField()
	length = forms.IntegerField(max_value=999) # Tour length, in minutes


class InitializeForm(forms.Form):
	now = datetime.datetime.now()
	months = [utilities.add_months(now, i) for i in range(0, 13)]
	months_choices = []
	for month in months:
		if not utilities.is_initialized(date=month):
			months_choices.append((month.strftime('%m/%Y'), month.strftime('%B %Y')))

	month = forms.ModelChoiceField(queryset=months_choices)

class UnclaimedForm(forms.Form):
	guide = forms.ModelChoiceField(queryset=models.Person.objects.all().order_by('last_name'), empty_label='Unclaimed', required=False)
	tour_id = forms.IntegerField(widget=forms.HiddenInput, required=True)

UnclaimedFormSet = formsets.formset_factory(UnclaimedForm, extra=0)
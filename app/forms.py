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
	time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'datepicker formcontrol'}, format="%m/%d/%Y %I:%M %p"), input_formats=["%m/%d/%Y %I:%M %p"])
	notes = forms.CharField(max_length=2000, widget=forms.Textarea, required=False)
	guide = forms.ModelChoiceField(queryset=models.Person.objects.filter(**(utilities.current_kwargs())).exclude(**(utilities.exclude_inactive_kwargs())).order_by('last_name', 'first_name'), empty_label='Unclaimed', required=False)
	source = forms.ChoiceField(choices=models.Tour.source_choices, required=False)
	missed = forms.BooleanField(required=False)
	late = forms.BooleanField(required=False)
	length = forms.IntegerField(max_value=999, required=False) # Tour length, in minutes

class MonthForm(forms.Form):
	guide = forms.ModelChoiceField(queryset=models.Person.objects.filter(**(utilities.current_kwargs())).exclude(**(utilities.exclude_inactive_kwargs())).order_by('last_name', 'first_name'), empty_label='Unclaimed', required=False)
	tour_id = forms.IntegerField(widget=forms.HiddenInput, required=True)

MonthFormSet = formsets.formset_factory(MonthForm, extra=0)
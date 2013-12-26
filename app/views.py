from django.http import Http404
from django.shortcuts import render
from app import models
import calendar
import datetime
from app.models import Tour, Person

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

	tours = models.Tour.objects.filter(time__month=month, time__year=year).order_by('time')
	
	try:
		weeks = calendar.Calendar().monthdays2calendar(year, month)
	
	# if month or year is not in range
	except ValueError:
		raise Http404()	

	canceled_days = models.CanceledDay.objects.filter(date__month=month, date__year=year).order_by('date')

	weeks_with_tours = []

	for week_index, week in enumerate(weeks):
		new_week = []
		for date, day in week:
			canceled = True if canceled_days.filter(date__day=date) else False
			new_week.append((date, day, tours.filter(time__day=date), canceled))
		weeks_with_tours.append(new_week)

	now = datetime.datetime.now()

	return render(request, 'month.html', { 'weeks': weeks_with_tours, 'now': now, 'month': month, 'year': year, 'month_name': calendar.month_name[now.month] })
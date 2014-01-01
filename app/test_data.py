# clear all data
from app import models, utilities
import datetime, calendar, pytz
from django.db.models import get_app, get_models
import csv
import pprint

def do(reset_people=False, reset_settings=False, people_file='key_roster.csv'):
	app = get_app('app')
	for model in get_models(app):
		if reset_people is False and (model == models.Person or model == models.InactiveSemester):
			pass
		elif reset_settings is False and (model == models.Setting or model == models.DefaultTour):
			pass
		else:
			model.objects.all().delete()
	
	print 'All tables cleared.'

	if reset_people is True:
		# import people
		people = []
		with open(people_file, 'rU') as csvfile:
			reader = csv.reader(csvfile, delimiter=',', quotechar='|', dialect=csv.excel_tab)
			counter = 0
			for row in reader:
				if counter == 0:
					counter =+ 1
					continue
				(first, last, class_num, email, secondary_email, house, cell, member_since) = row
				people.append({
					'first_name': first,
					'last_name': last,
					'year': int(class_num),
					'email': email,
					'secondary_email': secondary_email,
					'house': house,
					'phone': cell,
					'member_since': member_since
					})
				counter =+ 1
		for person in people:
			new_person = models.Person(**person)
			new_person.save()

		print '{0} people added.'.format(len(people))

	if reset_settings is True:
		# set up default tours
		utilities.add_default_tours()
		print 'Default tours added.'
		
	print 'Done.'
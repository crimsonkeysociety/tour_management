from django.db import models
import pytz, calendar

# Create your models here.

class Person(models.Model):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    email = models.EmailField()
    secondary_email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    year = models.IntegerField(max_length=4)
    notes = models.TextField(max_length=2000, blank=True)

    houses = ['Adams', 'Quincy', 'Lowell', 'Eliot', 'Kirkland', 'Winthrop', 'Mather', 'Leverett', 'Dunster', 'Cabot', 'Pforzheimer', 'Currier', 'Dudley']
    houses_choices = [(house, house) for house in houses]
    house = models.CharField(choices=houses_choices, max_length=50, blank=True, null=True)


    ADMIN = 2
    BOARD = 1
    REGULAR = 0

    permissions_choices = ( 
    						(ADMIN, "Site administrator"), 
    						(BOARD, "Board member"), 
    						(REGULAR, "Regular CKS member")
    					)
    person_permissions = models.IntegerField(max_length=1, choices=permissions_choices, default=REGULAR)


    def __unicode__(self):
        return u'{0} {1}'.format(self.first_name, self.last_name)

class Tour(models.Model):
        source_choices_flat = [
                            "Information Office",
                            "Marshall's Office",
                            "Alumni Association",
                            "Admissions Office",
                            "Visitas",
                            "Parents' Weekend",
                            "Comp",
                            "Other"
                        ]

        source_choices = [(i, i) for i in source_choices_flat]

	source = models.CharField(max_length=500, default="Information Office")
	guide = models.ForeignKey(Person, null=True, blank=True)
	time = models.DateTimeField()
	notes = models.TextField(max_length=2000, blank=True)
	missed = models.BooleanField(default=False)
	late = models.BooleanField(default=False)
	length = models.IntegerField(max_length=3, default=75) # Tour length, in minutes
        # true if tour was made during the initialization process
        default_tour = models.BooleanField(default=False)
    
        def is_missed(self):
            if self.missed:
                return True
            else:
                return False

        def is_late(self):
            if self.late:
                return True
            else:
                return False

        def is_unclaimed(self):
            if self.guide is None:
                return True
            else:
                return False

        def __unicode__(self):
            if self.guide is not None:
                return self.source + ', ' + self.time.astimezone(pytz.timezone('America/New_York')).strftime("%m/%d/%y %H:%M") + ', ' + self.guide.first_name + ' ' + self.guide.last_name
            else:
                return self.source + ', ' + self.time.astimezone(pytz.timezone('America/New_York')).strftime("%m/%d/%y %H:%M") + ', ' + 'Unclaimed'

class CanceledDay(models.Model):
    date = models.DateField()

class DefaultTour(models.Model):
    source = models.CharField(max_length=500, default="Information Office")
    time = models.DateTimeField()
    # 0 = Monday
    day_num = models.IntegerField(max_length=1)
    notes = models.TextField(max_length=2000, blank=True)
    length = models.IntegerField(max_length=3, default=75) # Tour length, in minutes

    def __unicode__(self):
        return self.source + ', ' + str(calendar.day_name[self.day_num]) + 's ' + self.time.astimezone(pytz.timezone('America/New_York')).strftime("%H:%M")

class InitializedMonth(models.Model):
    month = models.IntegerField(max_length=1)
    year = models.IntegerField(max_length=4)

    def __unicode__(self):
        return '{0} {1}'.format(calendar.month_name[self.month], self.year)
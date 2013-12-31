from django.db import models
import datetime, pytz, calendar
from app import utilities

# Create your models here.
from django.db import models
from django.db.models.query import QuerySet

class Person(models.Model):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    email = models.EmailField()
    secondary_email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    year = models.IntegerField(max_length=4)
    notes = models.TextField(max_length=2000, blank=True)

    # member since fall of...
    member_since = models.IntegerField(max_length=4)

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


    def is_active(self):
        semester = utilities.current_semester()
        now = datetime.datetime.now()
        year = now.year
        if self in utilities.active_members().filter(id=self.id):
            return True
        else:
            return False

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
	guide = models.ForeignKey(Person, null=True, blank=True, related_name='tours')
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


class Shift(models.Model):
    source_choices_flat = [
                            "TEACH",
                            "Parents' Weekend",
                            "Visitas",
                            "Comp",
                            "Other"
                        ]

    source_choices = [(i, i) for i in source_choices_flat]

    source = models.CharField(max_length=500)
    person = models.ForeignKey(Person, null=True, blank=True, related_name='shifts')
    time = models.DateTimeField()
    notes = models.TextField(max_length=2000, blank=True)
    missed = models.BooleanField(default=False)
    late = models.BooleanField(default=False)
    length = models.IntegerField(max_length=3, blank=True, null=True) # Tour length, in minutes

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
        if self.person is None:
            return True
        else:
            return False

    def __unicode__(self):
        if self.person is not None:
            return self.source + ', ' + self.time.astimezone(pytz.timezone('America/New_York')).strftime("%m/%d/%y %H:%M") + ', ' + self.person.first_name + ' ' + self.person.last_name
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

class Setting(models.Model):
    name = models.CharField(max_length=500)
    value = models.CharField(max_length=500)
    description = models.CharField(max_length=1000, null=True, blank=True)
    time_set = models.DateTimeField()

    def __unicode__(self):
        return '{0}: {1}'.format(self.name, self.value)

class InactiveSemester(models.Model):
    year = models.IntegerField(max_length=4)
    semesters_choices = [('fall', 'fall'), ('spring', 'spring')]
    semester = models.CharField(max_length=6, choices=semesters_choices)
    person = models.ForeignKey(Person, related_name='inactive_semesters')

    def __unicode__(self):
        return '{0} {1}: {2} {3}'.format(self.person.first_name, self.person.last_name, self.semester, self.year)
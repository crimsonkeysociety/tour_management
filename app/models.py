from django.db import models


# Create your models here.

class Person(models.Model):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    year = models.IntegerField(max_length=4)
    notes = models.TextField(max_length=2000, blank=True)


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
	source = models.CharField(max_length=100, default="Information Office")
	guide = models.ForeignKey(Person)
	time = models.DateTimeField()
	notes = models.TextField(max_length=2000, blank=True)
	missed = models.BooleanField(default=False)
	late = models.BooleanField(default=False)
	length = models.IntegerField(max_length=3, default=75) # Tour length, in minutes

	def __unicode__(self):
		return self.source + ', ' + self.time.strftime("%m/%d/%y %H:%M") + ', ' + self.guide.first_name + ' ' + self.guide.last_name

class CanceledDay(models.Model):
	date = models.DateField()
	canceled = models.BooleanField(default=True)
from django.contrib import admin
from app.models import *
from django import forms
# Register your models here.

class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'secondary_email', 'phone', 'year', 'house', 'person_permissions', 'notes')
    ordering = ('year', 'last_name', 'first_name',)

class TourAdmin(admin.ModelAdmin):
    list_display = ('source', 'time', 'guide', 'length', 'notes', 'missed', 'late', 'default_tour')

class DefaultTourAdmin(admin.ModelAdmin):
    list_display = ('source', 'time', 'day_num', 'length', 'notes')

admin.site.register(Person, PersonAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(CanceledDay)
admin.site.register(DefaultTour, DefaultTourAdmin)
admin.site.register(InitializedMonth)
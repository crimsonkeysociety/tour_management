from django.contrib import admin
from app.models import *
from django import forms
import re
from django.core.exceptions import *
# Register your models here.

class PersonAdminForm(forms.ModelForm):
	class Meta:
		model = Person
	
	def clean_phone(self):
		phone = self.cleaned_data['phone']
		if phone != '' and len(phone) < 10:
			raise ValidationError('Phone number is not 10 digits long.')
		elif phone == '':
			return phone
		else:

			phone = re.sub(r'\D', '', phone)

			if phone[0] == '1':
				phone = phone[1:]

			if len(phone) != 10:
				raise ValidationError('Phone number is not 10 digits long.')

		return phone

class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'secondary_email', 'phone', 'year', 'member_since', 'house', 'person_permissions', 'notes',)
    #list_display_links = ('last_name',)
    #list_editable = ('first_name',)
    ordering = ('-year', 'last_name', 'first_name',)
    form = PersonAdminForm

class TourAdmin(admin.ModelAdmin):
    list_display = ('source', 'time', 'guide', 'length', 'notes', 'missed', 'late', 'default_tour',)

class DefaultTourAdmin(admin.ModelAdmin):
    list_display = ('source', 'time', 'day_num', 'length', 'notes')

class SettingAdmin(admin.ModelAdmin):
	list_display = ('name', 'value', 'description')

class ShiftAdmin(admin.ModelAdmin):
    list_display = ('source', 'time', 'person', 'length', 'notes', 'missed', 'late',)


admin.site.register(Person, PersonAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(CanceledDay)
admin.site.register(DefaultTour, DefaultTourAdmin)
admin.site.register(InitializedMonth)
admin.site.register(Setting, SettingAdmin)
admin.site.register(InactiveSemester)
admin.site.register(Shift, ShiftAdmin)
from django.contrib import admin
from app.models import *
# Register your models here.

admin.site.register(Person)
admin.site.register(Tour)
admin.site.register(CanceledDay)
from app import models

# tours required per semester
TOURS_REQUIRED = models.Settings.objects.get(name='tours required')
SHIFTS_REQUIRED = models.Settings.objects.get(name='shifts required')
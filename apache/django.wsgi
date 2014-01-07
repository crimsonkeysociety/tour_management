import os
import sys

 path = '/srv/project/cks'
 if path not in sys.path:
     sys.path.insert(0, '/srv/project/cks')

 os.environ['DJANGO_SETTINGS_MODULE'] = 'cks.settings'

 import django.core.handlers.wsgi
 application = django.core.handlers.wsgi.WSGIHandler()
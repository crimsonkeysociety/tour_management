"""
WSGI config for cks project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cks.settings")
from django.conf import settings

if not settings.USE_CLING:
	
	from django.core.wsgi import get_wsgi_application
	application = get_wsgi_application()

else:

	from django.core.wsgi import get_wsgi_application
	from dj_static import Cling

	application = Cling(get_wsgi_application())
import importlib, os
from cks.settings_common import *
settings_local = importlib.import_module('cks.{}'.format(os.environ.get('DJANGO_SETTINGS')))
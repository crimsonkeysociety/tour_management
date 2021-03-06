# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Tour.date'
        db.alter_column(u'app_tour', 'date', self.gf('django.db.models.fields.DateTimeField')())

    def backwards(self, orm):

        # Changing field 'Tour.date'
        db.alter_column(u'app_tour', 'date', self.gf('django.db.models.fields.DateField')())

    models = {
        u'app.person': {
            'Meta': {'object_name': 'Person'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': 'None', 'max_length': '2000', 'blank': 'True'}),
            'person_permissions': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'year': ('django.db.models.fields.IntegerField', [], {'max_length': '4'})
        },
        u'app.tour': {
            'Meta': {'object_name': 'Tour'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'guide': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.Person']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'late': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'length': ('django.db.models.fields.IntegerField', [], {'default': '60', 'max_length': '3'}),
            'missed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['app']
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'InactiveSemester.id'
        db.delete_column(u'app_inactivesemester', u'id')


        # Changing field 'InactiveSemester.person'
        db.alter_column(u'app_inactivesemester', 'person_id', self.gf('django.db.models.fields.related.ForeignKey')(primary_key=True, to=orm['app.Person']))
        # Adding unique constraint on 'InactiveSemester', fields ['person']
        db.create_unique(u'app_inactivesemester', ['person_id'])


        # Changing field 'InactiveSemester.semester'
        db.alter_column(u'app_inactivesemester', 'semester', self.gf('django.db.models.fields.CharField')(max_length=6, primary_key=True))
        # Adding unique constraint on 'InactiveSemester', fields ['semester']
        db.create_unique(u'app_inactivesemester', ['semester'])


        # Changing field 'InactiveSemester.year'
        db.alter_column(u'app_inactivesemester', 'year', self.gf('django.db.models.fields.IntegerField')(max_length=4, primary_key=True))
        # Adding unique constraint on 'InactiveSemester', fields ['year']
        db.create_unique(u'app_inactivesemester', ['year'])


    def backwards(self, orm):
        # Removing unique constraint on 'InactiveSemester', fields ['year']
        db.delete_unique(u'app_inactivesemester', ['year'])

        # Removing unique constraint on 'InactiveSemester', fields ['semester']
        db.delete_unique(u'app_inactivesemester', ['semester'])

        # Removing unique constraint on 'InactiveSemester', fields ['person']
        db.delete_unique(u'app_inactivesemester', ['person_id'])


        # User chose to not deal with backwards NULL issues for 'InactiveSemester.id'
        raise RuntimeError("Cannot reverse this migration. 'InactiveSemester.id' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'InactiveSemester.id'
        db.add_column(u'app_inactivesemester', u'id',
                      self.gf('django.db.models.fields.AutoField')(primary_key=True),
                      keep_default=False)


        # Changing field 'InactiveSemester.person'
        db.alter_column(u'app_inactivesemester', 'person_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Person']))

        # Changing field 'InactiveSemester.semester'
        db.alter_column(u'app_inactivesemester', 'semester', self.gf('django.db.models.fields.CharField')(max_length=6))

        # Changing field 'InactiveSemester.year'
        db.alter_column(u'app_inactivesemester', 'year', self.gf('django.db.models.fields.IntegerField')(max_length=4))

    models = {
        u'app.canceledday': {
            'Meta': {'object_name': 'CanceledDay'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'app.defaulttour': {
            'Meta': {'object_name': 'DefaultTour'},
            'day_num': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {'default': '75', 'max_length': '3'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'default': "'Information Office'", 'max_length': '500'}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'app.inactivesemester': {
            'Meta': {'object_name': 'InactiveSemester'},
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'inactive_semesters'", 'primary_key': 'True', 'to': u"orm['app.Person']"}),
            'semester': ('django.db.models.fields.CharField', [], {'max_length': '6', 'primary_key': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'max_length': '4', 'primary_key': 'True'})
        },
        u'app.initializedmonth': {
            'Meta': {'object_name': 'InitializedMonth'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'year': ('django.db.models.fields.IntegerField', [], {'max_length': '4'})
        },
        u'app.person': {
            'Meta': {'object_name': 'Person'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'house': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'person_permissions': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'secondary_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'max_length': '4'})
        },
        u'app.settings': {
            'Meta': {'object_name': 'Settings'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'app.tour': {
            'Meta': {'object_name': 'Tour'},
            'default_tour': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'guide': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tours'", 'null': 'True', 'to': u"orm['app.Person']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'late': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'length': ('django.db.models.fields.IntegerField', [], {'default': '75', 'max_length': '3'}),
            'missed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'default': "'Information Office'", 'max_length': '500'}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['app']
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'InactiveSemester'
        db.create_table(u'app_inactivesemester', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')(max_length=4)),
            ('semester', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='inactive_semesters', to=orm['app.Person'])),
        ))
        db.send_create_signal(u'app', ['InactiveSemester'])

        # Deleting field 'Person.active'
        db.delete_column(u'app_person', 'active')


    def backwards(self, orm):
        # Deleting model 'InactiveSemester'
        db.delete_table(u'app_inactivesemester')

        # Adding field 'Person.active'
        db.add_column(u'app_person', 'active',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'inactive_semesters'", 'to': u"orm['app.Person']"}),
            'semester': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'year': ('django.db.models.fields.IntegerField', [], {'max_length': '4'})
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
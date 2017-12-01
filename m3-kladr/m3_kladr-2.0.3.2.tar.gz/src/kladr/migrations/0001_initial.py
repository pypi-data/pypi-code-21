# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'KladrGeo'
        db.create_table('kladr_kladrgeo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kladr.KladrGeo'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40, db_index=True)),
            ('socr', self.gf('django.db.models.fields.CharField')(max_length=10, db_index=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=13, db_index=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('gni', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('uno', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('okato', self.gf('django.db.models.fields.CharField')(max_length=11)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('level', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('kladr', ['KladrGeo'])

        # Adding model 'KladrStreet'
        db.create_table('kladr_kladrstreet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kladr.KladrGeo'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40, db_index=True)),
            ('socr', self.gf('django.db.models.fields.CharField')(max_length=10, db_index=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=17, db_index=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('gni', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('uno', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('okato', self.gf('django.db.models.fields.CharField')(max_length=11)),
        ))
        db.send_create_signal('kladr', ['KladrStreet'])


    def backwards(self, orm):
        
        # Deleting model 'KladrGeo'
        db.delete_table('kladr_kladrgeo')

        # Deleting model 'KladrStreet'
        db.delete_table('kladr_kladrstreet')


    models = {
        'kladr.kladrgeo': {
            'Meta': {'object_name': 'KladrGeo'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '13', 'db_index': 'True'}),
            'gni': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'}),
            'okato': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kladr.KladrGeo']", 'null': 'True', 'blank': 'True'}),
            'socr': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'uno': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        },
        'kladr.kladrstreet': {
            'Meta': {'object_name': 'KladrStreet'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '17', 'db_index': 'True'}),
            'gni': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'}),
            'okato': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kladr.KladrGeo']", 'null': 'True', 'blank': 'True'}),
            'socr': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'uno': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        }
    }

    complete_apps = ['kladr']

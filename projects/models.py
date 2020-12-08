from django.db import models

# Create your models here.

class UserFiles(models.Model):
	id = models.AutoField(primary_key=True)
	user = models.ForeignKey('users.AuthUser', models.DO_NOTHING, db_column='user', blank=True, null=True)
	filename = models.TextField(blank=True, null=True)
	filepath = models.TextField(blank=True, null=True)
	
	class Meta:
		managed = False
		db_table = 'user_files'
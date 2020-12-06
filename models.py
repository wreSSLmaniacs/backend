# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Blog(models.Model):
    blog_id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=128)
    content = models.TextField()
    author = models.ForeignKey('RatedUsers', models.DO_NOTHING, db_column='author')

    class Meta:
        managed = False
        db_table = 'blog'


class Contest(models.Model):
    contest_id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=128)
    blog = models.ForeignKey(Blog, models.DO_NOTHING, blank=True, null=True)
    patricipant_count = models.BigIntegerField(blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    isrunning = models.BooleanField(db_column='isRunning', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'contest'


class ContestUser(models.Model):
    perf_id = models.BigIntegerField(primary_key=True)
    contest = models.ForeignKey(Contest, models.DO_NOTHING)
    user = models.ForeignKey('RatedUsers', models.DO_NOTHING, blank=True, null=True)
    ranking = models.IntegerField(blank=True, null=True)
    net_score = models.IntegerField(blank=True, null=True)
    del_rating = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contest_user'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Problems(models.Model):
    problem_id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=128, blank=True, null=True)
    statement = models.TextField(blank=True, null=True)
    testcases = models.TextField(blank=True, null=True)  # This field type is a guess.
    no_subs = models.BigIntegerField(blank=True, null=True)
    author = models.ForeignKey('RatedUsers', models.DO_NOTHING, db_column='author')
    ref_blog = models.ForeignKey(Blog, models.DO_NOTHING, db_column='ref_blog', blank=True, null=True)
    feat_contest = models.ForeignKey(Contest, models.DO_NOTHING, db_column='feat_contest', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'problems'


class RatedUsers(models.Model):
    username = models.CharField(primary_key=True, max_length=64)
    rating = models.IntegerField(blank=True, null=True)
    pdirec = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'rated_users'


class Submissions(models.Model):
    submission_id = models.BigIntegerField(primary_key=True)
    problem = models.ForeignKey(Problems, models.DO_NOTHING)
    user = models.ForeignKey(RatedUsers, models.DO_NOTHING)
    code = models.TextField()  # This field type is a guess.
    language = models.CharField(max_length=16)
    verdict = models.CharField(max_length=16)
    score = models.IntegerField()
    time_of_submission = models.DateTimeField()
    contest_submission = models.BooleanField()
    contest = models.ForeignKey(ContestUser, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'submissions'


class UserFiles(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='user', blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    filepath = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_files'


class Users(models.Model):
    user_fk = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='user_fk', blank=True, null=True)
    image = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'

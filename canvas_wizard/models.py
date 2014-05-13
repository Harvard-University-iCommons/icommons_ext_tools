from django.db import models

'''
Models for managing Canvas Templates
''' 

class Template(models.Model):
    template_id = models.IntegerField(primary_key=True, db_column='template_id')
    term = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    canvas_course_id = models.IntegerField()
    date_created = models.DateTimeField()

    class Meta:
        db_table = u'"TEMPLATES"'
        managed = False

    def __unicode__(self):
        return self.template_id

class TemplateAccount(models.Model):
    sis_account_id = models.CharField(primary_key=True, max_length=20)
    account_name = models.CharField(max_length=50)
    can_use_wizard = models.CharField(max_length=1)

    class Meta:
        db_table = u'"TEMPLATE_ACCOUNTS"'
        managed = False

    def __unicode__(self):
        return self.sis_account_id


class TemplateUsers(models.Model):
    user_id = models.CharField(primary_key=True, max_length=20, db_column='user_id')
    sis_account_id = models.CharField(max_length=20)
    can_manage_templates = models.CharField(max_length=1)
    can_bulk_create_courses = models.CharField(max_length=1)
    can_manage_users = models.CharField(max_length=1)
    date_added = models.DateTimeField()

    class Meta:
        db_table = u'"TEMPLATE_USERS"'
        managed = False

    def __unicode__(self):
        return self.user_id

class TemplateGroup(models.Model):
    group_id = models.CharField(primary_key=True, max_length=20)
    sis_account_id = models.CharField(max_length=20)
    can_manage_templates = models.CharField(max_length=1)
    can_bulk_create_courses = models.CharField(max_length=1)
    date_added = models.DateTimeField()

    class Meta:
        db_table = u'"TEMPLATE_GROUPS"'
        managed = False

    def __unicode__(self):
        return self.group_id

class TemplateAccessList(models.Model):
    access_id = models.IntegerField(primary_key=True, db_column='access_id')
    sisaccount = models.ForeignKey(TemplateAccount, db_column='sis_account_id', related_name='account')
    template = models.ForeignKey(Template, db_column='template_id', related_name='template_access')
    templateuser = models.ForeignKey(TemplateUsers, db_column='user_id', related_name='users')
    date_created = models.DateTimeField()

    class Meta:
        db_table = u'"TEMPLATE_ACCESS_LIST"'
        managed = False

    def __unicode__(self):
        return self.access_id

class TemplateCourseDelegates(models.Model):
    delegate_id = models.IntegerField(primary_key=True, db_column='delegate_id')
    course_instance_id = models.CharField(max_length=20)
    delegate_user_id = models.CharField(max_length=20)
    date_added = models.DateTimeField()

    class Meta:
        db_table = u'"TEMPLATE_COURSE_DELEGATES"'
        managed = False

    def __unicode__(self):
        return self.course_instance_id + ':' + self.delegate_user_id




from django.db import models
from django.utils import timezone

class SchoolCodeMapping(models.Model):
    """
    Note: This is a copy of the School_code_mapping DB Table from RPT database.
    IDDB has a different set of school codes for students and a completely
    different set for employees. This mapping table reconciles both of those
    into a single table. It is a bit complex  to append the school data to the
    ldap_people_plus view and since this rarely changes, we are fetching and
    maintaining a copy locally

    TODO: Revisit and fix this when we move to new people service
    """

    student_school_code = models.CharField(max_length=2)
    student_school_desc = models.CharField(max_length=64)
    employee_school_code = models.CharField(max_length=10)


    class Meta:
        db_table = u'school_code_mapping'

    def __unicode__(self):
        return self.student_school_code

class Acceptance(models.Model):
    """
    This is a table used to track and store Qulatrics user acceptance of terms
    of service
    """
    user_id = models.CharField(max_length=200, primary_key=True)
    acceptance_date = models.DateTimeField()
    ip_address = models.CharField(max_length=100)

    class Meta:
        db_table = u'acceptance'

    def __unicode__(self):
        return self.id


class QualtricsUser(models.Model):
    univ_id = models.CharField(max_length=32)
    qualtrics_id = models.CharField(max_length=32)
    manually_updated = models.BooleanField()
    qualtrics_division = models.CharField(max_length=50, null=True)
    qualtrics_user_type = models.CharField(max_length=50, null=True)
    lpp_division = models.CharField(max_length=50, null=True)
    lpp_user_type = models.CharField(max_length=50, null=True)
    iam_division = models.CharField(max_length=50, null=True)
    iam_user_type = models.CharField(max_length=50, null=True)
    last_login = models.DateTimeField(null=True)

    class Meta:
        db_table = u'qualtrics_user'

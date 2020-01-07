from django.db import models


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
        db_table = 'school_code_mapping'

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
        db_table = 'acceptance'

    def __unicode__(self):
        return self.id


class QualtricsUser(models.Model):
    univ_id = models.CharField(max_length=32)
    qualtrics_id = models.CharField(max_length=32)
    manually_updated = models.BooleanField()

    class Meta:
        db_table = 'qualtrics_user'

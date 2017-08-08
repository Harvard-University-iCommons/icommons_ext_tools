from django.db import models


class SchoolCodeMapping(models.Model):
    """
    Note: This is a copy of the School_code_mapping DB Table from RPT database.
    IDDB has a different set of school codes for students and a completely
    different set for employees. This mapping table reconciles both of those
    into a single table. It is a bit complex  to append the school data to the
    ldap_people_plus view and since this rarely changes, we are fetching and
    maintaining a copy locally
    """

    student_school_code = models.CharField(max_length=2)
    student_school_desc = models.CharField(max_length=64)
    employee_school_code = models.CharField(max_length=10)


    class Meta:
        db_table = u'school_code_mapping'

    def __unicode__(self):
        return self.student_school_code


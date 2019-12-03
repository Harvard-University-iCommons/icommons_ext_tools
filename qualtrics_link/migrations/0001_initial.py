# -*- coding: utf-8 -*-


from django.db import migrations, models, transaction


SCHOOL_CODE_DATA = [

    ('01',	'OBSOLETE Harvard and Radcliffe Colleges', ''),
    ('24',	'Graduate School of Business Administration', 'HBS'),
    ('25',	'Graduate School of Business Administration', 'HBS'),
    ('32',	'Graduate School of Arts and Sciences',	'FAS'),
    ('33',	'Harvard College', 'FAS'),
    ('35',	'School of Dental Medicine', 'SDM'),
    ('36',	'School of Dental Medicine', 'SDM'),
    ('37',	'Graduate School of Design', 'GSD'),
    ('38',	'American Repertory Theater', 'ART'),
    ('39',	'Divinity School', 'DIV'),
    ('41',	'Graduate School of Education', 'GSE'),
    ('57',	'Law School', 'HLS'),
    ('58',	'Law School', 'HLS'),
    ('60',	'Medical School', 'HMS'),
    ('70',	'Harvard Kennedy School', 'KSG'),
    ('72',	'School of Public Health', 'SPH'),
    ('92',	'OBSOLETE Non-Registered Health Insurance',	''),
    ('AM',	'Graduate School of Business Administration', 'HBS'),
    ('EX',	'Division of Continuing Education - Extension',	'DCE'),
    ('PM',	'Graduate School of Business Administration', 'HBS'),
    ('SP',	'Graduate School of Arts and Sciences - Special', 'FAS'),
    ('SU',	'Division of Continuing Education - Summer', 'DCE'),
    ('TU',	'Trade Union Program', ''),
    ('XB',	'Graduate School of Business Administration - Executive Education',	'HBS'),
    ('XK',	'Harvard Kennedy School - Executive Education',	'KSG'),
    ('XE',	'Graduate School of Education - Executive Education', 'GSE'),
    ('XL',	'Law School - Executive Education',	'HLS'),
    ('XM',	'Medical School - Executive Education',	'HMS'),
    ('XV',	'Divinity School - Executive Education', 'DIV'),
    ('XH',	'School of Public Health - Executive Education', 'SPH'),
    ('XD',	'School of Dental Medicine - Executive Education', 'SDM'),
    ('XS',	'Graduate School of Design - Executive Education', 'GSD'),
]

def populate_school_codes(apps, schema_editor):

    SchoolCodeMapping = apps.get_model('qualtrics_link', 'SchoolCodeMapping')
    fields = ('student_school_code', 'student_school_desc', 'employee_school_code')

    for code in SCHOOL_CODE_DATA:
        SchoolCodeMapping.objects.create(**dict(list(zip(fields, code))))


def reverse_school_load(apps, schema_editor):
    # LtiPermission = apps.get_model('lti_permissions', 'LtiPermission')
    # LtiPermission.objects.filter(permission='publish_courses').delete()
    SchoolCodeMapping = apps.get_model('qualtrics_link', 'SchoolCodeMapping')
    SchoolCodeMapping.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
         migrations.CreateModel(
            name='SchoolCodeMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False,
                                        auto_created=True, primary_key=True)),
                ('student_school_code', models.CharField(max_length=2)),
                ('student_school_desc', models.CharField(max_length=64)),
                ('employee_school_code', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'school_code_mapping',
            },
        ),
        migrations.RunPython(
            code=populate_school_codes,
            reverse_code=reverse_school_load,
        ),
    ]

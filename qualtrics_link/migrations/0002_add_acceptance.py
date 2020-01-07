# -*- coding: utf-8 -*-


from django.db import migrations, models, transaction


class Migration(migrations.Migration):

    dependencies = [
        ('qualtrics_link', '0001_initial'),
    ]

    user_id = models.CharField(max_length=200)
    acceptance_date = models.DateTimeField()
    ip_address = models.CharField(max_length=100)

    operations = [
         migrations.CreateModel(
            name='Acceptance',
            fields=[
                ('user_id', models.CharField(max_length=30, primary_key=True)),
                ('acceptance_date', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'acceptance',
            },
         )
    ]


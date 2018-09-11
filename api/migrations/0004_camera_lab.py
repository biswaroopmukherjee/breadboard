# Generated by Django 2.1.1 on 2018-09-11 06:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_run_workday'),
    ]

    operations = [
        migrations.AddField(
            model_name='camera',
            name='lab',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cameras', to='api.Lab'),
        ),
    ]

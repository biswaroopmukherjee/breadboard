# Generated by Django 2.1.1 on 2019-03-13 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20190313_1821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='bad_shot',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Was this image a bad shot?'),
        ),
    ]

# Generated by Django 4.2.6 on 2023-11-27 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0033_alter_contactform_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordereditems',
            name='modified_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]

# Generated by Django 4.2.6 on 2023-11-20 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_authentication', '0006_rename_is_liste_address_is_listed'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='referal_code',
            field=models.CharField(default='BNMBSJ', max_length=20),
            preserve_default=False,
        ),
    ]

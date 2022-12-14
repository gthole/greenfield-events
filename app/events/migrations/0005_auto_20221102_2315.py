# Generated by Django 3.0 on 2022-11-03 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_recurringevent'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='event',
            name='events_even_venue_i_f3b114_idx',
        ),
        migrations.RenameField(
            model_name='event',
            old_name='venue',
            new_name='source',
        ),
        migrations.RenameField(
            model_name='recurringevent',
            old_name='venue',
            new_name='source',
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['source'], name='events_even_source__90c628_idx'),
        ),
    ]

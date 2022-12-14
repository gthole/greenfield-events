# Generated by Django 3.0 on 2022-10-23 20:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EventSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('spider', models.CharField(blank=True, max_length=255, null=True)),
                ('default_location', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(max_length=255)),
                ('url', models.URLField(max_length=500)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(null=True)),
                ('location', models.CharField(max_length=255)),
                ('all_day', models.BooleanField(default=False)),
                ('created_dttm', models.DateTimeField(auto_now_add=True)),
                ('updated_dttm', models.DateTimeField(auto_now=True)),
                ('start_dttm', models.DateTimeField(blank=True, null=True)),
                ('end_dttm', models.DateTimeField(blank=True, null=True)),
                ('canceled', models.BooleanField(default=False)),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='events.EventSource')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['-start_dttm'], name='events_even_start_d_61ec94_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['source'], name='events_even_source__90c628_idx'),
        ),
    ]

# Generated by Django 2.2.10 on 2020-02-20 19:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='newsletter title')),
                ('slug', models.SlugField(unique=True)),
                ('email', models.EmailField(help_text='Sender e-mail', max_length=254, verbose_name='e-mail')),
                ('sender', models.CharField(help_text='Sender name', max_length=200, verbose_name='sender')),
            ],
            options={
                'verbose_name': 'newsletter',
                'verbose_name_plural': 'newsletters',
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_field', models.EmailField(blank=True, db_column='email', db_index=True, max_length=254, null=True, verbose_name='e-mail')),
                ('name_field', models.CharField(blank=True, db_column='name', help_text='optional', max_length=30, null=True, verbose_name='name')),
                ('create_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('newsletter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newsletter.Newsletter', verbose_name='newsletter')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'subscription',
                'verbose_name_plural': 'subscriptions',
                'unique_together': {('user', 'email_field', 'newsletter')},
            },
        ),
    ]
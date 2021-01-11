# Generated by Django 3.1.4 on 2021-01-11 17:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('register_and_login', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dog_name', models.CharField(max_length=50)),
                ('breed', models.CharField(max_length=100)),
                ('size', models.CharField(choices=[('S', 'small'), ('M', 'medium'), ('B', 'big')], default='S', max_length=1)),
                ('short_description', models.CharField(max_length=300)),
                ('image', models.ImageField(default='profile_pics/dog_default.jpg', upload_to='profile_pics/')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='register_and_login.profile')),
            ],
        ),
    ]

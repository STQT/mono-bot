# Generated migration

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_add_multilingual_gift_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='privacypolicy',
            name='content_ru',
        ),
        migrations.RemoveField(
            model_name='privacypolicy',
            name='content_uz_latin',
        ),
    ]


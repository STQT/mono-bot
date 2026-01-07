# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_add_gift_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='broadcastmessage',
            name='region_min_latitude',
            field=models.FloatField(blank=True, help_text='Minimal kenglik (latitude) filtri', null=True, verbose_name='Min kenglik'),
        ),
        migrations.AddField(
            model_name='broadcastmessage',
            name='region_max_latitude',
            field=models.FloatField(blank=True, help_text='Maksimal kenglik (latitude) filtri', null=True, verbose_name='Max kenglik'),
        ),
        migrations.AddField(
            model_name='broadcastmessage',
            name='region_min_longitude',
            field=models.FloatField(blank=True, help_text='Minimal uzunlik (longitude) filtri', null=True, verbose_name='Min uzunlik'),
        ),
        migrations.AddField(
            model_name='broadcastmessage',
            name='region_max_longitude',
            field=models.FloatField(blank=True, help_text='Maksimal uzunlik (longitude) filtri', null=True, verbose_name='Max uzunlik'),
        ),
        migrations.AddField(
            model_name='broadcastmessage',
            name='language_filter',
            field=models.CharField(blank=True, choices=[('uz_latin', "O'zbek (Lotin)"), ('uz_cyrillic', "O'zbek (Kirill)"), ('ru', 'Русский')], max_length=15, null=True, verbose_name="Til bo'yicha filtr"),
        ),
    ]


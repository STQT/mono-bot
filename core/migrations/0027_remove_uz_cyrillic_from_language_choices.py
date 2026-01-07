# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_replace_region_coords_with_filter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='broadcastmessage',
            name='language_filter',
            field=models.CharField(
                blank=True,
                choices=[('uz_latin', "O'zbek (Lotin)"), ('ru', 'Русский')],
                max_length=15,
                null=True,
                verbose_name="Til bo'yicha filtr"
            ),
        ),
    ]


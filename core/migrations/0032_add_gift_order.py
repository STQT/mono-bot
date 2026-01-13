# Generated manually on 2026-01-08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_historicaladmincontactsettings_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='gift',
            name='order',
            field=models.IntegerField(
                default=0,
                help_text="Kichikroq raqam yuqorida ko'rsatiladi",
                verbose_name='Tartib raqami'
            ),
        ),
        migrations.AlterModelOptions(
            name='gift',
            options={
                'ordering': ['order', 'points_cost', 'name_uz_latin'],
                'verbose_name': 'Sovg\'a',
                'verbose_name_plural': 'Sovg\'alar ro\'yxati',
            },
        ),
    ]

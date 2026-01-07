# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_add_region_filters_to_broadcast'),
    ]

    operations = [
        # Удаляем старые поля координат
        migrations.RemoveField(
            model_name='broadcastmessage',
            name='region_min_latitude',
        ),
        migrations.RemoveField(
            model_name='broadcastmessage',
            name='region_max_latitude',
        ),
        migrations.RemoveField(
            model_name='broadcastmessage',
            name='region_min_longitude',
        ),
        migrations.RemoveField(
            model_name='broadcastmessage',
            name='region_max_longitude',
        ),
        # Добавляем новое поле выбора региона
        migrations.AddField(
            model_name='broadcastmessage',
            name='region_filter',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', 'Barcha viloyatlar'),
                    ('tashkent_city', 'Toshkent shahri'),
                    ('tashkent_region', 'Toshkent viloyati'),
                    ('andijan', 'Andijon viloyati'),
                    ('bukhara', 'Buxoro viloyati'),
                    ('jizzakh', 'Jizzax viloyati'),
                    ('kashkadarya', 'Qashqadaryo viloyati'),
                    ('navoi', 'Navoiy viloyati'),
                    ('namangan', 'Namangan viloyati'),
                    ('samarkand', 'Samarqand viloyati'),
                    ('surkhandarya', 'Surxondaryo viloyati'),
                    ('syrdarya', 'Sirdaryo viloyati'),
                    ('fergana', 'Farg\'ona viloyati'),
                    ('khorezm', 'Xorazm viloyati'),
                    ('karakalpakstan', 'Qoraqalpog\'iston Respublikasi'),
                ],
                help_text='Tanlangan viloyatdagi foydalanuvchilarga xabar yuborish uchun viloyatni tanlang. Bo\'sh qoldirilsa, barcha viloyatlarga yuboriladi.',
                max_length=50,
                null=True,
                verbose_name='Viloyat bo\'yicha filtr'
            ),
        ),
    ]


# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_add_multilingual_gift_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminContactSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_type', models.CharField(choices=[('telegram', 'Telegram username'), ('phone', 'Telefon raqami'), ('link', 'Havola (URL)')], default='telegram', help_text='Telegram username, telefon raqami yoki havola', max_length=20, verbose_name='Kontakt turi')),
                ('contact_value', models.CharField(help_text="Telegram username (@ belgisisiz), telefon raqami (+998901234567) yoki to'liq havola (https://...)", max_length=255, verbose_name='Kontakt qiymati')),
                ('is_active', models.BooleanField(default=True, verbose_name='Faol')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yangilangan')),
            ],
            options={
                'verbose_name': 'Admin kontakt sozlamalari',
                'verbose_name_plural': 'Admin kontakt sozlamalari',
                'ordering': ['-updated_at'],
            },
        ),
    ]


# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_alter_giftredemption_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='privacypolicy',
            name='pdf_uz_latin',
            field=models.FileField(blank=True, help_text='PDF файл политики конфиденциальности для узбекского языка (латиница)', null=True, upload_to='privacy_policy/', verbose_name='PDF файл (O\'zbek lotin)'),
        ),
        migrations.AddField(
            model_name='privacypolicy',
            name='pdf_ru',
            field=models.FileField(blank=True, help_text='PDF файл политики конфиденциальности для русского языка', null=True, upload_to='privacy_policy/', verbose_name='PDF файл (Ruscha)'),
        ),
        migrations.AlterField(
            model_name='privacypolicy',
            name='content_ru',
            field=models.TextField(blank=True, help_text='Текстовый контент (необязательно, если загружен PDF)', verbose_name='Kontent (Ruscha)'),
        ),
        migrations.AlterField(
            model_name='privacypolicy',
            name='content_uz_latin',
            field=models.TextField(blank=True, help_text='Текстовый контент (необязательно, если загружен PDF)', verbose_name='Kontent (O\'zbek lotin)'),
        ),
    ]


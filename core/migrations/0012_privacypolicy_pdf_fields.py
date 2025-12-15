# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_qrcode_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='privacypolicy',
            name='pdf_uz_latin',
            field=models.FileField(blank=True, help_text='PDF файл политики конфиденциальности для узбекского языка (латиница)', null=True, upload_to='privacy_policy/', verbose_name='PDF файл (O\'zbek lotin)'),
        ),
        migrations.AddField(
            model_name='privacypolicy',
            name='pdf_uz_cyrillic',
            field=models.FileField(blank=True, help_text='PDF файл политики конфиденциальности для узбекского языка (кириллица)', null=True, upload_to='privacy_policy/', verbose_name='PDF файл (O\'zbek kirill)'),
        ),
        migrations.AddField(
            model_name='privacypolicy',
            name='pdf_ru',
            field=models.FileField(blank=True, help_text='PDF файл политики конфиденциальности для русского языка', null=True, upload_to='privacy_policy/', verbose_name='PDF файл (Ruscha)'),
        ),
        migrations.AlterField(
            model_name='privacypolicy',
            name='content_uz_latin',
            field=models.TextField(blank=True, help_text='Текстовый контент для узбекского языка (латиница). Если загружен PDF, текст будет использован как подпись.', verbose_name='Kontent (O\'zbek lotin)'),
        ),
        migrations.AlterField(
            model_name='privacypolicy',
            name='content_uz_cyrillic',
            field=models.TextField(blank=True, help_text='Текстовый контент для узбекского языка (кириллица). Если загружен PDF, текст будет использован как подпись.', verbose_name='Kontent (O\'zbek kirill)'),
        ),
        migrations.AlterField(
            model_name='privacypolicy',
            name='content_ru',
            field=models.TextField(blank=True, help_text='Текстовый контент для русского языка. Если загружен PDF, текст будет использован как подпись.', verbose_name='Kontent (Ruscha)'),
        ),
    ]


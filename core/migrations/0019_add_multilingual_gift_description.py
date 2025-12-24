# Generated manually

from django.db import migrations, models


def migrate_description_data(apps, schema_editor):
    """Переносит данные из description в description_uz_latin."""
    Gift = apps.get_model('core', 'Gift')
    for gift in Gift.objects.all():
        if hasattr(gift, 'description') and gift.description:
            gift.description_uz_latin = gift.description
            gift.save(update_fields=['description_uz_latin'])


def reverse_migrate_description_data(apps, schema_editor):
    """Обратная миграция - переносит данные обратно."""
    Gift = apps.get_model('core', 'Gift')
    for gift in Gift.objects.all():
        if hasattr(gift, 'description_uz_latin') and gift.description_uz_latin:
            # В обратной миграции мы не можем установить description, так как поле будет удалено
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_add_privacy_policy_pdf_fields'),
    ]

    operations = [
        # Добавляем новые мультиязычные поля
        migrations.AddField(
            model_name='gift',
            name='description_uz_latin',
            field=models.TextField(blank=True, verbose_name='Tavsif (O\'zbek lotin)'),
        ),
        migrations.AddField(
            model_name='gift',
            name='description_ru',
            field=models.TextField(blank=True, verbose_name='Tavsif (Ruscha)'),
        ),
        # Переносим данные из старого поля description в description_uz_latin
        migrations.RunPython(
            code=migrate_description_data,
            reverse_code=reverse_migrate_description_data,
        ),
        # Удаляем старое поле description
        migrations.RemoveField(
            model_name='gift',
            name='description',
        ),
    ]


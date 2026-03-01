# Generated manually - make Promotion.title optional

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_add_broadcast_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promotion',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Sarlavha'),
        ),
    ]

# Generated manually - VideoInstruction: 4 videos (electrician/seller x UZ/RU) + thumbnails

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_promotion_title_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='videoinstruction',
            name='video_electrician_uz',
            field=models.FileField(blank=True, help_text="Video fayl elektriklar uchun o'zbek tilida", null=True, upload_to='video_instructions/', verbose_name="Video — Elektrik (O'zbek)"),
        ),
        migrations.AddField(
            model_name='videoinstruction',
            name='video_electrician_ru',
            field=models.FileField(blank=True, help_text='Video fayl elektriklar uchun rus tilida', null=True, upload_to='video_instructions/', verbose_name='Video — Elektrik (Ruscha)'),
        ),
        migrations.AddField(
            model_name='videoinstruction',
            name='thumb_electrician_uz',
            field=models.ImageField(blank=True, help_text="JPEG, max 320x320, 200KB. Oldindan ko'rinish uchun.", null=True, upload_to='video_instructions/thumbs/', verbose_name="Thumbnail — Elektrik (O'zbek)"),
        ),
        migrations.AddField(
            model_name='videoinstruction',
            name='thumb_electrician_ru',
            field=models.ImageField(blank=True, help_text='JPEG, max 320x320, 200KB. Превью для видео.', null=True, upload_to='video_instructions/thumbs/', verbose_name='Thumbnail — Elektrik (Ruscha)'),
        ),
        migrations.AddField(
            model_name='videoinstruction',
            name='video_seller_uz',
            field=models.FileField(blank=True, help_text="Video fayl tadbirkorlar uchun o'zbek tilida", null=True, upload_to='video_instructions/', verbose_name="Video — Tadbirkor (O'zbek)"),
        ),
        migrations.AddField(
            model_name='videoinstruction',
            name='video_seller_ru',
            field=models.FileField(blank=True, help_text='Video fayl tadbirkorlar uchun rus tilida', null=True, upload_to='video_instructions/', verbose_name='Video — Tadbirkor (Ruscha)'),
        ),
        migrations.AddField(
            model_name='videoinstruction',
            name='thumb_seller_uz',
            field=models.ImageField(blank=True, help_text='JPEG, max 320x320, 200KB.', null=True, upload_to='video_instructions/thumbs/', verbose_name='Thumbnail — Tadbirkor (O\'zbek)'),
        ),
        migrations.AddField(
            model_name='videoinstruction',
            name='thumb_seller_ru',
            field=models.ImageField(blank=True, help_text='JPEG, max 320x320, 200KB.', null=True, upload_to='video_instructions/thumbs/', verbose_name='Thumbnail — Tadbirkor (Ruscha)'),
        ),
        migrations.AddField(
            model_name='videoinstruction',
            name='file_id_electrician_uz',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='file_id Elektrik UZ'),
        ),
        migrations.AddField(
            model_name='videoinstruction',
            name='file_id_electrician_ru',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='file_id Elektrik RU'),
        ),
        migrations.AddField(
            model_name='videoinstruction',
            name='file_id_seller_uz',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='file_id Tadbirkor UZ'),
        ),
        migrations.AddField(
            model_name='videoinstruction',
            name='file_id_seller_ru',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='file_id Tadbirkor RU'),
        ),
        migrations.RemoveField(model_name='videoinstruction', name='video_uz_latin'),
        migrations.RemoveField(model_name='videoinstruction', name='video_ru'),
        migrations.RemoveField(model_name='videoinstruction', name='file_id_uz_latin'),
        migrations.RemoveField(model_name='videoinstruction', name='file_id_ru'),
        # HistoricalVideoInstruction
        migrations.AddField(model_name='historicalvideoinstruction', name='video_electrician_uz', field=models.TextField(blank=True, max_length=100, null=True)),
        migrations.AddField(model_name='historicalvideoinstruction', name='video_electrician_ru', field=models.TextField(blank=True, max_length=100, null=True)),
        migrations.AddField(model_name='historicalvideoinstruction', name='thumb_electrician_uz', field=models.TextField(blank=True, max_length=100, null=True)),
        migrations.AddField(model_name='historicalvideoinstruction', name='thumb_electrician_ru', field=models.TextField(blank=True, max_length=100, null=True)),
        migrations.AddField(model_name='historicalvideoinstruction', name='video_seller_uz', field=models.TextField(blank=True, max_length=100, null=True)),
        migrations.AddField(model_name='historicalvideoinstruction', name='video_seller_ru', field=models.TextField(blank=True, max_length=100, null=True)),
        migrations.AddField(model_name='historicalvideoinstruction', name='thumb_seller_uz', field=models.TextField(blank=True, max_length=100, null=True)),
        migrations.AddField(model_name='historicalvideoinstruction', name='thumb_seller_ru', field=models.TextField(blank=True, max_length=100, null=True)),
        migrations.AddField(model_name='historicalvideoinstruction', name='file_id_electrician_uz', field=models.CharField(blank=True, max_length=255, null=True)),
        migrations.AddField(model_name='historicalvideoinstruction', name='file_id_electrician_ru', field=models.CharField(blank=True, max_length=255, null=True)),
        migrations.AddField(model_name='historicalvideoinstruction', name='file_id_seller_uz', field=models.CharField(blank=True, max_length=255, null=True)),
        migrations.AddField(model_name='historicalvideoinstruction', name='file_id_seller_ru', field=models.CharField(blank=True, max_length=255, null=True)),
        migrations.RemoveField(model_name='historicalvideoinstruction', name='video_uz_latin'),
        migrations.RemoveField(model_name='historicalvideoinstruction', name='video_ru'),
        migrations.RemoveField(model_name='historicalvideoinstruction', name='file_id_uz_latin'),
        migrations.RemoveField(model_name='historicalvideoinstruction', name='file_id_ru'),
    ]

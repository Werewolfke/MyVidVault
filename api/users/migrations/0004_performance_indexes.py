from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0003_alter_profile_default_bookmark_collection_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='bookmark',
            index=models.Index(fields=['video', 'user', 'created_at'], name='bm_vid_usr_crt_idx'),
        ),
        migrations.AddIndex(
            model_name='bookmark',
            index=models.Index(fields=['channel', 'created_at'], name='bm_channel_crt_idx'),
        ),
    ]

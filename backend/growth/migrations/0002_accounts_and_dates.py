import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def delete_anonymous_rows(apps, schema_editor):
    """Drop the shared demo workspace so every remaining row belongs to a student."""
    for model_name in ('Task', 'WeeklyScore', 'StudySession', 'WeeklyReview', 'UserSettings'):
        model = apps.get_model('growth', model_name)
        model.objects.filter(user__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('growth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='usersettings',
            name='timezone',
            field=models.CharField(default='Asia/Dhaka', max_length=64),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='student_name',
            field=models.CharField(blank=True, default='', max_length=128),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='aspiration',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='major',
            field=models.CharField(blank=True, default='', max_length=128),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='gpa_target',
            field=models.CharField(blank=True, default='', max_length=32),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='current_execution_rate',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='weekly_study_pr_hours',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='longest_session_pr_minutes',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='weekly_intention',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.RunPython(delete_anonymous_rows, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='task',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='weeklyscore',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weekly_scores', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='studysession',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='study_sessions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='weeklyreview',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weekly_reviews', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='benchmark_settings', to=settings.AUTH_USER_MODEL),
        ),
    ]

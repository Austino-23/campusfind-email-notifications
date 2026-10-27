from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('core', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='MatchNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient_email', models.EmailField(max_length=254)),
                ('match_score', models.FloatField(default=0)),
                ('email_sent', models.BooleanField(default=False)),
                ('email_sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('found_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='match_notifications_as_found', to='core.item')),
                ('lost_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='match_notifications_as_lost', to='core.item')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddConstraint(model_name='matchnotification', constraint=models.UniqueConstraint(fields=('lost_item', 'found_item'), name='unique_lost_found_notification')),
    ]

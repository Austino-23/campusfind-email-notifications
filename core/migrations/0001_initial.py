# Baseline migration matching the original CampusFind Item and Claim tables.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('report_type', models.CharField(choices=[('lost', 'Lost'), ('found', 'Found')], max_length=5)),
                ('category', models.CharField(choices=[('electronics', 'Electronics'), ('documents', 'Documents'), ('personal', 'Personal items'), ('bags', 'Bags'), ('books', 'Books'), ('clothing', 'Clothing'), ('other', 'Other')], max_length=20)),
                ('location', models.CharField(max_length=180)),
                ('item_date', models.DateField()),
                ('description', models.TextField()),
                ('contact_email', models.EmailField(blank=True, max_length=254)),
                ('photo', models.FileField(blank=True, null=True, upload_to='item_photos/')),
                ('is_resolved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reported_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Claim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('claimant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_claims', to=settings.AUTH_USER_MODEL)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='claims', to='core.item')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddConstraint(model_name='claim', constraint=models.UniqueConstraint(fields=('item', 'claimant'), name='unique_claim_per_user_item')),
    ]

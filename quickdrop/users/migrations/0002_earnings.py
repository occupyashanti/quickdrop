from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('deliveries', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Earnings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('earning_type', models.CharField(choices=[('DELIVERY', 'Delivery Completion'), ('BONUS', 'Performance Bonus'), ('TIP', 'Customer Tip'), ('OTHER', 'Other')], default='DELIVERY', max_length=20)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('delivery', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='earnings', to='deliveries.delivery')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='earnings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Earnings',
                'db_table': 'worker_earnings',
                'ordering': ['-timestamp'],
            },
        ),
    ]

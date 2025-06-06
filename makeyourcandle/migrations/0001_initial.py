# Generated by Django 4.2.9 on 2025-03-03 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MakeYourCandle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purpose', models.CharField(help_text='Purpose of the candle (e.g., Baby Shower, Wedding Gift, etc.)', max_length=255)),
                ('quantity', models.CharField(help_text='Number of candles (e.g., 1-10, 11-20, etc.)', max_length=50)),
                ('scent', models.CharField(help_text='Preferred scent (e.g., Vanilla, Mango, etc.)', max_length=100)),
                ('jar_color', models.CharField(help_text='Preferred candle jar color (e.g., Frosted Red, Frosted White, etc.)', max_length=100)),
                ('special_labeling', models.CharField(help_text='Do you need special labeling? (Yes/No)', max_length=3)),
                ('custom_message', models.CharField(blank=True, help_text='Custom message for labeling (if applicable)', max_length=255, null=True)),
                ('delivery_timeline', models.CharField(help_text='When do you need the candles by? (e.g., Within a week, 1-2 weeks, etc.)', max_length=100)),
                ('additional_notes', models.TextField(blank=True, help_text='Any additional notes or requests', null=True)),
                ('email', models.EmailField(help_text="Customer's email address", max_length=254)),
                ('phone_number', models.CharField(help_text="Customer's phone number", max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp when the order was created')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Timestamp when the order was last updated')),
            ],
            options={
                'verbose_name': 'Make Your Candle Order',
                'verbose_name_plural': 'Make Your Candle Orders',
            },
        ),
    ]

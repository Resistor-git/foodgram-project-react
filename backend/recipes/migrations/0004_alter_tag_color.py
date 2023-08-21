# Generated by Django 3.2.20 on 2023-08-21 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_rename_colour_code_tag_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(help_text='Color code, example: #49B64E', max_length=7, unique=True),
        ),
    ]

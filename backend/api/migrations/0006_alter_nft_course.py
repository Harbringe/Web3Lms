# Generated by Django 4.2.7 on 2025-06-04 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0005_alter_nft_course"),
    ]

    operations = [
        migrations.AlterField(
            model_name="nft",
            name="course",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to="api.course"
            ),
        ),
    ]

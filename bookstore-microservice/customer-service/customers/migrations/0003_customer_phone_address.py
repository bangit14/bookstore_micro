from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("customers", "0002_userprofile"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="phone",
            field=models.CharField(max_length=20, blank=True, default=""),
        ),
        migrations.AddField(
            model_name="customer",
            name="address",
            field=models.TextField(blank=True, default=""),
        ),
    ]

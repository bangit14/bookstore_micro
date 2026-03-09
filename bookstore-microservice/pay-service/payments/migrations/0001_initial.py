from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name="Payment", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("order_id", models.IntegerField()), ("amount", models.DecimalField(decimal_places=2, max_digits=10)), ("method", models.CharField(default="cod", max_length=60)), ("status", models.CharField(choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed")], default="pending", max_length=20)), ("transaction_id", models.CharField(blank=True, max_length=120)), ("created_at", models.DateTimeField(auto_now_add=True))])]

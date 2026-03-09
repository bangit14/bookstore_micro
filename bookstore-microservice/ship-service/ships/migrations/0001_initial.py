from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name="Shipment", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("order_id", models.IntegerField()), ("shipping_address", models.CharField(max_length=255)), ("status", models.CharField(choices=[("pending", "Pending"), ("shipping", "Shipping"), ("delivered", "Delivered"), ("failed", "Failed")], default="pending", max_length=20)), ("tracking_code", models.CharField(blank=True, max_length=120)), ("created_at", models.DateTimeField(auto_now_add=True))])]

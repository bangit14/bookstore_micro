import django.db.models.deletion
from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="Order", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("customer_id", models.IntegerField()), ("total_amount", models.DecimalField(decimal_places=2, max_digits=10)), ("status", models.CharField(choices=[("created", "Created"), ("paid", "Paid"), ("shipping", "Shipping"), ("completed", "Completed"), ("cancelled", "Cancelled")], default="created", max_length=20)), ("shipping_address", models.CharField(max_length=255)), ("created_at", models.DateTimeField(auto_now_add=True))]),
        migrations.CreateModel(name="OrderItem", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("product_id", models.IntegerField()), ("quantity", models.IntegerField(default=1)), ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)), ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="orders.order"))]),
    ]

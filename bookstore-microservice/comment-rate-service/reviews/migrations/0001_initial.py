from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name="Review", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("customer_id", models.IntegerField()), ("product_id", models.IntegerField()), ("rating", models.IntegerField()), ("comment", models.TextField(blank=True)), ("created_at", models.DateTimeField(auto_now_add=True))])]

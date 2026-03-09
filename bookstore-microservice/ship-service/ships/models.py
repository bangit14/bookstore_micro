from django.db import models
class Shipment(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("shipping", "Shipping"), ("delivered", "Delivered"), ("failed", "Failed")]
    order_id = models.IntegerField()
    shipping_address = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    tracking_code = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

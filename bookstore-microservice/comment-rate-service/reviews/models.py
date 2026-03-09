from django.db import models
class Review(models.Model):
    customer_id = models.IntegerField()
    product_id = models.IntegerField()
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

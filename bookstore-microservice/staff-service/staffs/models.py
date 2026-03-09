from django.db import models
class Staff(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=120)
    position = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

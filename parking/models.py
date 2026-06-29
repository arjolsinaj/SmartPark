from django.db import models


class Parking(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    total_spaces = models.IntegerField()
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Vehicle(models.Model):
    parking = models.ForeignKey(Parking, on_delete=models.CASCADE)
    plate_number = models.CharField(max_length=20)
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    is_inside = models.BooleanField(default=True)
    fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return self.plate_number

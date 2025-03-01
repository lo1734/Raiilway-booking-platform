from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import time
from calendar import Day

# ✅ Custom User Model
class CustomUser(AbstractUser):
    pass  # Add extra fields if needed

class Day(models.Model):
    name = models.CharField(max_length=10, unique=True)  # Example: "Monday"

    def __str__(self):
        return self.name
# ✅ Train Model
class Train(models.Model):
    train_number = models.CharField(max_length=10, unique=True)
    train_name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    total_seats = models.IntegerField()

    boarding_time = models.TimeField(default=time(0, 0))
    departure_time = models.TimeField(default=time(23,59))

    # ✅ Boolean fields for weekdays
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)

    def get_running_days(self):
        days = []
        if self.monday: days.append("Monday")
        if self.tuesday: days.append("Tuesday")
        if self.wednesday: days.append("Wednesday")
        if self.thursday: days.append("Thursday")
        if self.friday: days.append("Friday")
        if self.saturday: days.append("Saturday")
        if self.sunday: days.append("Sunday")
        return ", ".join(days)

    def __str__(self):
        return f"{self.train_name} ({self.train_number})"

# ✅ Intermediate Station Model
class IntermediateStation(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="stations")
    station_name = models.CharField(max_length=100)
    arrival_time = models.TimeField()
    departure_time = models.TimeField()

    def __str__(self):
        return self.station_name
# class IntermediateStation(models.Model):
#     train = models.ForeignKey(Train, on_delete=models.CASCADE)
#     station_name = models.CharField(max_length=100)
#     arrival_time = models.TimeField()
#     departure_time = models.TimeField()
#
#     def __str__(self):
#         return self.station_name

# ✅ Booking Model
class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    journey_date = models.DateField()
    seats_booked = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.train.train_name}"



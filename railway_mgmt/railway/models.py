from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import time
from calendar import Day

# ✅ Custom User Model
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # Ensure unique emails

    def __str__(self):
        return self.username # Add extra fields if needed

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
    running_days = models.ManyToManyField(Day)

    # ✅ Boolean fields for weekdays
    DAYS_OF_WEEK = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    ]
    running_days = models.ManyToManyField(Day)

    def get_running_days(self):
        return ", ".join(self.running_days.values_list("name", flat=True))

    def __str__(self):
        return f"{self.train_name} ({self.train_number})"
    # def __str__(self):
    #     return f"{self.train_name} ({self.train_number})({self.train.DAYS_OF_WEEK})"

# ✅ Intermediate Station Model
class IntermediateStation(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="stations")
    station_name = models.CharField(max_length=100)
    arrival_time = models.TimeField()
    departure_time = models.TimeField()

    is_source = models.BooleanField(default=False)
    is_destination = models.BooleanField(default=False)

    class Meta:
        ordering=["arrival_time"]
    def __str__(self):
        return f"{self.station_name}(Train: {self.train.train_name})"


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
    from_station = models.CharField(max_length=100,default="Not Assigned")
    to_station = models.CharField(max_length=100,default="Not Assigned")
    journey_date = models.DateField()
    seats_booked = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.train.train_name}({self.from_station} to {self.to_station})"


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Train)
def add_source_and_destination(sender, instance, created, **kwargs):
    if created:  # ✅ Only add when a new train is created
        # ✅ Check if source and destination already exist in IntermediateStation (avoid duplicates)
        existing_source = IntermediateStation.objects.filter(train=instance, station_name=instance.source, is_source=True).exists()
        existing_destination = IntermediateStation.objects.filter(train=instance, station_name=instance.destination, is_destination=True).exists()

        if not existing_source:
            IntermediateStation.objects.create(
                train=instance,
                station_name=instance.source,
                arrival_time=instance.boarding_time,  # Arrival is train's start time
                departure_time=instance.boarding_time,  # Departure is also the start time
                is_source=True
            )

        if not existing_destination:
            IntermediateStation.objects.create(
                train=instance,
                station_name=instance.destination,
                arrival_time=instance.departure_time,  # Arrival is train's end time
                departure_time=instance.departure_time,  # Departure is also the end time
                is_destination=True
            )

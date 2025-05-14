from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # Ensure unique emails

    def __str__(self):
        return self.username # Add extra fields if needed

class Day(models.Model):
    name = models.CharField(max_length=10, unique=True)  # Example: "Monday"

    def __str__(self):
        return self.name

from django.db import models
from datetime import time

class Train(models.Model):
    train_number = models.CharField(max_length=10, unique=True)
    train_name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    total_seats = models.IntegerField()

    boarding_time = models.TimeField(default=time(0, 0))
    departure_time = models.TimeField(default=time(23, 59))

    # ✅ Boolean fields for weekdays (kept as checkboxes)
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

class IntermediateStation(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="stations")
    station_name = models.CharField(max_length=100)
    arrival_time = models.TimeField()
    departure_time = models.TimeField()

    is_source = models.BooleanField(default=False)
    is_destination = models.BooleanField(default=False)

    def __str__(self):
        return self.station_name

class TrainGraph(models.Model):
    train=models.ForeignKey(Train, on_delete=models.CASCADE,related_name="edges")
    from_station=models.ForeignKey(IntermediateStation,on_delete=models.CASCADE,related_name="departures")
    to_station=models.ForeignKey(IntermediateStation,on_delete=models.CASCADE,related_name="arrivals")
    available_seats=models.IntegerField()

    class Meta:
        unique_together=("train","from_station","to_station")

    def __str__(self):
        return f"{self.from_station.station_name} -> {self.to_station.station_name} : {self.available_seats} seats"

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

@receiver(post_save,sender=Train)
def create_train_graph(sender,instance,created, **kwargs):
    if created:
        stations=IntermediateStation.objects.filter(train=instance).order_by("arrival_time")
        total_seats=instance.total_seats

        for i in range(len(stations)-1) :
            TrainGraph.objects.create(
                train=instance,
                from_station=stations[i],
                to_station=stations[i+1],
                available_seats=total_seats
            )
@receiver(post_save,sender=Booking)
def update_seats_on_booking(sender,instance,created,**kwargs):
    if created:
        train=instance.train,
        from_station=IntermediateStation.objects.filter(
            train=train,
            station_name=instance.from_station
        ).first()
        to_station=IntermediateStation.objects.filter(
            train=train,
            station_name=instance.to_station
        ).first()

        if from_station and to_station:
            path_edges=TrainGraph.objects.filter(
                train=train,
                from_station__arrival_time__gte=from_station.arrival_time,
                to_station__arrival_time__lte=to_station.arrival_time
            )

            for edge in path_edges:
                edge.available_seats-=instance.seats_booked
                edge.save()

def get_available_seats(train, from_station, to_station):
    path_edges=TrainGraph.objects.filter(
        train=train,
        from_station__arrival_time__gte=from_station.arrival_time,
        to_station__arrival_time__lte=to_station.arrival_time
    )

    return min(e.available_seats for e in path_edges) if path_edges.exist() else 0

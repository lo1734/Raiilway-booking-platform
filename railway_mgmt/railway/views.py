from django.contrib.auth import authenticate, login, logout
from .models import Train, Booking, IntermediateStation
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
import random
from django.shortcuts import render
import datetime
from django.core.exceptions import ObjectDoesNotExist

# Home Page View
def home(request):
    return render(request, 'railway/home.html')

# def search_trains(request):
#     source = request.GET.get('source', '').strip()
#     destination = request.GET.get('destination', '').strip()
#     travel_date = request.GET.get('date', '').strip()
#
#     if not source or not destination or not travel_date:
#         return render(request, "railway/search_trains.html", {"error": "Missing parameters"})
#
#     # Get the day of the week (Monday, Tuesday, etc.)
#     selected_day = datetime.datetime.strptime(travel_date, "%Y-%m-%d").strftime("%A").lower()
#
#     # Find trains running on this day OR through intermediate stations
#     trains = Train.objects.filter(
#         source=source,
#         destination=destination,
#         # travel_date=datetime.date
#     ).filter(**{selected_day: True})  # Check the Boolean field for the weekday
#
#     # Also check trains with intermediate stations
#     trains_with_intermediate = Train.objects.filter(
#         stations__station_name=destination
#     ).filter(**{selected_day: True}).distinct()
#
#     # Combine both queries
#     available_trains = trains | trains_with_intermediate
#
#     return render(request, "railway/search_trains.html", {
#         "source": source,
#         "destination": destination,
#         "travel_date": travel_date,
#         "trains": available_trains
#     })

otp_storage = {}

from django.middleware.csrf import get_token

def get_csrf_token(request):
    return JsonResponse({"csrfToken": get_token(request)})
def send_otp(request):
    email = request.GET.get('email')
    if not email:
        return JsonResponse({"error": "Email is required"}, status=400)

    otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
    otp_storage[email] = otp  # Store OTP (in production, store it securely)

    print(f"OTP for {email}: {otp}")  # Debugging purpose, replace with actual email sending
    return JsonResponse({"success": True, "message": "OTP sent successfully!"})


def verify_otp(request):
    email = request.GET.get('email')
    entered_otp = request.GET.get('otp')

    if not email or not entered_otp:
        return JsonResponse({"error": "Email and OTP are required"}, status=400)

    correct_otp = otp_storage.get(email)

    if correct_otp and str(correct_otp) == entered_otp:
        return JsonResponse({"success": True, "message": "OTP verified successfully!"})
    else:
        return JsonResponse({"error": "Incorrect OTP"}, status=400)

def register_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already exists"}, status=400)

        # Create and save user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        login(request, user)  # Auto-login user after registration
        return JsonResponse({"message": "Registration successful!"})

    return render(request, "railway/register.html")


# Login View
def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=400)
    return render(request, 'railway/login.html')


# Logout View
def user_logout(request):
    logout(request)
    return redirect('home')


# Registration View
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)
        user = User.objects.create_user(username, email, password)
        user.save()
        return redirect('login')
    return render(request, 'railway/register.html')

# def search_trains(request):
#     source = request.GET.get('source', '').strip()
#     destination = request.GET.get('destination', '').strip()
#     travel_date = request.GET.get('date', '').strip()
#
#     if not source or not destination or not travel_date:
#         return render(request, "railway/search_trains.html", {"error": "Missing parameters"})
#
#     # Convert date into the weekday (e.g., Monday)
#     travel_day = datetime.datetime.strptime(travel_date, "%Y-%m-%d").strftime("%A").lower()
#
#     # Find direct trains
#     available_trains = Train.objects.filter(
#         source=source,
#         destination=destination,
#         **{travel_day: True}  # Check the Boolean field for the weekday
#     )
#
#     # Find trains that have an intermediate station matching the destination
#     trains_with_intermediate = Train.objects.filter(
#         stations__station_name=destination,
#         **{travel_day: True}
#     ).distinct()
#
#     # Combine both queries
#     available_trains = available_trains | trains_with_intermediate
#
#     return render(request, "railway/search_trains.html", {
#         "source": source,
#         "destination": destination,
#         "travel_date": travel_date,
#         "trains": available_trains
#     })


# Train Booking API

def search_trains(request):
    source = request.GET.get("source", "").strip()
    destination = request.GET.get("destination", "").strip()
    travel_date = request.GET.get("date", "").strip()

    if not source or not destination or not travel_date:
        return render(request, "railway/search_trains.html", {"error": "Missing parameters"})

    # Get the day of the week (Monday, Tuesday, etc.)
    travel_day = datetime.datetime.strptime(travel_date, "%Y-%m-%d").strftime("%A").lower()

    # Get direct trains
    direct_trains = Train.objects.filter(
        source=source,
        destination=destination,
        # travel_day=datetime.date
        ** {travel_day: True}  # Check the boolean field for the weekday
    )

    # Get trains with intermediate stations
    # intermediate_trains = Train.objects.filter(
    #     stations__station_name__in=[source,destination],
    #     # stations__station_name=source,
    #     **{travel_day: True}
    # ).distinct()

    # intermediate_trains = IntermediateStation.objects.filter(
    #     stations__station_name__in=[source, destination],
    #     # stations__station_name=source,
    #     **{travel_day: True}
    # ).distinct()

    source_stations=IntermediateStation.objects.filter(station_name=source).select_related("train")
    destination_stations=IntermediateStation.objects.filter(station_name=destination).select_related("train")
    valid_intermediate_trains = []
    # for train in intermediate_trains:
    #     station_names = list(train.stations.values_list("station_name", flat=True))
    #
    #     # if destination in station_names and station_names.index(source) < station_names.index(destination):
    #     #     valid_intermediate_trains.append(train)
    #     if source in station_names and destination in station_names and station_names.index(source) < station_names.index(destination):
    #         valid_intermediate_trains.append(train)

    for source_station in source_stations:
        train=source_station.train

        destination_station=destination_stations.filter(train=train).first()
        if destination_station:
            source_index=train.intermediatestation_set.filter(train=train,station_name=source).value_list("id",flat=True)[0]
            destination_index=train.intermediatestation_set.filter(train=train,station_nmae=destination).value_list("id",flat=True)[0]

            if(source_index<destination_index):
                valid_intermediate_trains.append(train)

    available_trains = list(direct_trains) + list(valid_intermediate_trains)
    #   available_trains = list(direct_trains)
    return render(request, "railway/search_trains.html", {
        "source": source,
        "destination": destination,
        "travel_date": travel_date,
        "trains": available_trains
    })

def book_ticket(request):
    if request.method == "POST":
        user = request.user
        train_id = request.POST.get('train_id')
        seats = int(request.POST.get('seats'))
        train = Train.objects.get(id=train_id)

        if train.total_seats >= seats:
            Booking.objects.create(user=user, train=train, journey_date=request.POST.get('date'), seats_booked=seats)
            train.total_seats -= seats
            train.save()
            return JsonResponse({"message": "Booking Successful!"})
        else:
            return JsonResponse({"error": "Not enough seats available"}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)


# OTP Generation for Email Verification
def generate_otp(request):
    if request.method == "GET":
        otp = random.randint(100000, 999999)
        request.session['otp'] = otp
        return JsonResponse({"otp": otp})
    return JsonResponse({"error": "Invalid request"}, status=400)


from django.contrib.auth import authenticate, login, logout
from .models import Train, Booking, IntermediateStation, CustomUser, TrainGraph
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
import random
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.middleware.csrf import get_token


# Home Page View
def home(request):
    return render(request, 'railway/home.html')

otp_storage = {}

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


# Login View
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if AJAX request
                return JsonResponse({"message": "Login successful"}, status=200)
            return redirect('home')
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=400)

    return render(request, 'railway/login.html', {"csrf_token": get_token(request)})


# Logout View
def user_logout(request):
    logout(request)
    return redirect('home')


# Registration View

def register(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '').strip()

            if not username or not email or not password:
                return JsonResponse({"error": "All fields are required."}, status=400)

            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({"error": "Username already exists"}, status=400)

            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email already exists"}, status=400)

            # ✅ Create and save user
            user = CustomUser.objects.create_user(username=username, email=email, password=password)
            user.save()

            return JsonResponse({"message": "Registration successful! Please log in."}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

    # return JsonResponse({"error": "Invalid request method."}, status=405)
    return render(request,"railway/register.html")



def search_trains(request):
    source = request.GET.get("source", "").strip().lower()
    destination = request.GET.get("destination", "").strip().lower()
    travel_date = request.GET.get("date", "").strip()

    if not source or not destination or not travel_date:
        return render(request, "railway/search_trains.html", {"error": "Missing parameters"})

    # Get the day of the week (Monday, Tuesday, etc.)
    travel_day = datetime.datetime.strptime(travel_date, "%Y-%m-%d").strftime("%A").lower()

    # Get direct trains
    direct_trains = Train.objects.filter(
        source=source,
        destination=destination,
        **{travel_day: True}  # Check the boolean field for the weekday
    ).distinct()
    print(f" Direct Trains Found: {direct_trains}")

    source_trains = (Train.objects.filter(
        source=source,
        **{travel_day: True}
    ).distinct())

    intermediate_source_stations=IntermediateStation.objects.filter(
        station_name=source,
        train__in=Train.objects.filter(**{travel_day:True})
    ).select_related("train").order_by("id")
    print(f"️Source Trains (Direct Start): {source_trains}")
    print(f"Source Trains (Intermediate Start): {[t.train for t in intermediate_source_stations]}")

    destination_trains=Train.objects.filter(
        destination=destination,
        **{travel_day: True}
    ).distinct()


    valid_intermediate_trains = []
    for source_station in intermediate_source_stations:
        train=source_station.train
        station_list=IntermediateStation.objects.filter(train=train).order_by("arrival_time")
        station_names=[s.station_name.lower() for s in station_list]
        print(f"Checking Train: {train.train_name}, Stations: {station_names}")

        if source in station_names and destination in station_names:
            if station_names.index(source)<station_names.index(destination):
                valid_intermediate_trains.append(train)

    print(f" Valid Intermediate Trains: {valid_intermediate_trains}")

    available_trains = list(set(direct_trains) | set(valid_intermediate_trains))

    # print(f"Searching trains from {source} to {destination} on {travel_day}")
    # print(f"Direct Trains Found: {direct_trains}")
    # print(f"Source Trains: {source_trains}")
    # print(f"Destination Trains: {destination_trains}")
    # print(f"Valid Intermediate Trains: {valid_intermediate_trains}")
    return render(request, "railway/search_trains.html", {
        "source": source,
        "destination": destination,
        "travel_date": travel_date,
        "trains": available_trains
    })



def book_ticket(request):
    if request.method == "POST":
        try:
            user = request.user
            data = request.POST  # Extract data

            train_id = data.get('train_id', '').strip()
            from_station = data.get('from_station', '').strip().lower()
            to_station = data.get('to_station', '').strip().lower()
            journey_date = data.get('travel_date', '').strip()
            seats_str = data.get('seats', '1').strip()

            try:
                train_id = int(train_id)
                train = Train.objects.get(id=train_id)
            except (ValueError, Train.DoesNotExist):
                return JsonResponse({"error": "Invalid train ID or train not found"}, status=400)

            try:
                seats = int(seats_str)
                if seats <= 0:
                    return JsonResponse({"error": "Seats must be a positive number"}, status=400)
            except ValueError:
                return JsonResponse({"error": f"Invalid seat count: {seats_str}"}, status=400)

            available_seats = get_available_seats(train, from_station, to_station, journey_date)
            if available_seats is None:
                return JsonResponse({"error": "Invalid station selection"}, status=400)

            if available_seats >= seats:
                Booking.objects.create(
                    user=user,
                    train=train,
                    from_station=from_station,
                    to_station=to_station,
                    journey_date=journey_date,
                    seats_booked=seats
                )
                return JsonResponse({"message": "Booking Successful!"})
            else:
                return JsonResponse({"error": "Not enough seats available"}, status=400)

        except Exception as e:
            print(f"DEBUG: Unexpected error - {str(e)}")
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

def get_available_seats(train, from_station, to_station, journey_date):
    try:
        # Fetch available seats for the given train and stations
        train_graph = TrainGraph.objects.get(
            train=train,
            from_station__station_name__iexact=from_station,  # Case-insensitive match
            to_station__station_name__iexact=to_station
        )
        return train_graph.available_seats
    except TrainGraph.DoesNotExist:
        return None  # Indicates invalid station selection

def booking_confirmation(request):
    return render(request, "railway/booking_confirmation.html")


def train_route(request,train_id):
    train = get_object_or_404(Train, id=train_id)
    route_stations=IntermediateStation.objects.filter(train=train).order_by("arrival_time")
    return render(request,"railway/train_route.html",{'train':train,'route_stations':route_stations})

def available_trains(request):
    trains = Train.objects.all()
    return render(request, 'available_trains.html', {'trains': trains})


def generate_otp(request):
    if request.method == "GET":
        otp = random.randint(100000, 999999)
        request.session['otp'] = otp
        return JsonResponse({"otp": otp})
    return JsonResponse({"error": "Invalid request"}, status=400)

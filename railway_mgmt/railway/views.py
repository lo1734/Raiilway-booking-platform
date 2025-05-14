from django.contrib.auth import authenticate, login, logout
from .models import Train, Booking, IntermediateStation, CustomUser, Passenger
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
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum



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


@login_required(login_url='/login/')
def book_ticket(request):
    if request.method == "POST":
        # Verbose logging
        user=request.user
        if not user.is_authenticated:
            redirect('login.html')
        print("DEBUG: Full POST data:", dict(request.POST))
        print("DEBUG: Raw request body:", request.body)

        try:
            # user = request.user
            train_id = request.POST.get('train_id')
            from_station = request.POST.get('from_station', '').strip()
            to_station = request.POST.get('to_station', '').strip()
            travel_date = request.POST.get('travel_date', '').strip()

            request.session['booking_data'] = {
                'train_id': train_id,
                'from_station': from_station,
                'to_station': to_station,
                'travel_date': travel_date
            }

            return redirect('passenger_details')

        except Exception as e:
            print(f"DEBUG: Unexpected error - {str(e)}")
            return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)


# def book_ticket(request):
#     if request.method == "POST":
#         # Verbose logging
#         user=request.user
#         if not user.is_authenticated:
#             redirect('login.html')
#         print("DEBUG: Full POST data:", dict(request.POST))
#         print("DEBUG: Raw request body:", request.body)
#
#         try:
#             user = request.user
#             train_id = request.POST.get('train_id')
#             from_station = request.POST.get('from_station', '').strip()
#             to_station = request.POST.get('to_station', '').strip()
#             journey_date = request.POST.get('travel_date', '').strip()
#
#             # Seats extraction with multiple fallback mechanisms
#             # seats_str = request.POST.get('seats', '')
#             # print(f"DEBUG: Seats value extracted: {seats_str}")
#
#             # Comprehensive seats validation
#             # if not seats_str:
#             #     # Try alternative extraction methods
#             #     seats_str = request.POST.getlist('seats', ['1'])[0]
#             #     print(f"DEBUG: Seats after alternative extraction: {seats_str}")
#
#             # try:
#             #     seats = int(seats_str)
#             #     if seats <= 0:
#             #         return JsonResponse({"error": "Number of seats must be positive"}, status=400)
#             # except (ValueError, TypeError):
#             #     return JsonResponse({"error": f"Invalid seat count: {seats_str}"}, status=400)
#
#             # Rest of booking logic remains the same
#             try:
#                 train = Train.objects.get(id=train_id)
#             except Train.DoesNotExist:
#                 return JsonResponse({"error": "Train not found"}, status=404)
#
#             available_seats = get_available_seats(train, from_station, to_station, journey_date)
#
#             if available_seats is None:
#                 return JsonResponse({"error": "Invalid station selection"}, status=400)
#
#             if available_seats >= seats:
#                 Booking.objects.create(
#                     user=user,
#                     train=train,
#                     from_station=from_station,
#                     to_station=to_station,
#                     journey_date=journey_date,
#                     seats_booked=seats
#                 )
#                 return JsonResponse({"message": "Booking Successful!"})
#             else:
#                 return JsonResponse({"error": "Not enough seats available"}, status=400)
#
#         except Exception as e:
#             print(f"DEBUG: Unexpected error - {str(e)}")
#             return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)
#
#     return JsonResponse({"error": "Invalid request method"}, status=400)

def get_available_seats(train, from_station, to_station, journey_date):
    """
    Returns the number of available seats for the given segment (from_station to to_station).
    """
    # Validate input parameters
    if not from_station or not to_station:
        print(f"DEBUG: Invalid station selection. From: {from_station}, To: {to_station}")
        return None

    # Get all stations for this train in order
    train_stations = list(train.stations.order_by('station_order'))

    # Find station indices
    try:
        from_index = next(i for i, station in enumerate(train_stations) if station.station_name == from_station)
        to_index = next(i for i, station in enumerate(train_stations) if station.station_name == to_station)
    except StopIteration:
        print(f"DEBUG: Stations not found in train route. From: {from_station}, To: {to_station}")
        print(f"DEBUG: Available stations: {[station.station_name for station in train_stations]}")
        return None

    # Validate station order
    if from_index >= to_index:
        print(f"DEBUG: Invalid station order. From index: {from_index}, To index: {to_index}")
        return None

    total_seats = train.total_seats

    # Get all bookings for this train on the selected date
    bookings = Booking.objects.filter(train=train, journey_date=journey_date)

    # Initialize seat usage tracking
    seat_usage = [0] * len(train_stations)

    # Calculate seat usage
    for booking in bookings:
        try:
            booking_from_index = next(
                i for i, station in enumerate(train_stations) if station.station_name == booking.from_station)
            booking_to_index = next(
                i for i, station in enumerate(train_stations) if station.station_name == booking.to_station)
        except StopIteration:
            # Skip bookings with invalid stations
            continue

        # Mark seats as used for the booking's route
        for i in range(booking_from_index, booking_to_index):
            seat_usage[i] += booking.seats_booked

    # Calculate available seats for the requested segment
    segment_seat_usage = seat_usage[from_index:to_index]

    if not segment_seat_usage:
        print("DEBUG: No seat usage data found for segment")
        return total_seats

    max_segment_usage = max(segment_seat_usage)
    available_seats = total_seats - max_segment_usage

    print(
        f"DEBUG: Available seats calculation - Total: {total_seats}, Segment Usage: {segment_seat_usage}, Available: {available_seats}")

    return max(available_seats, 0)
def booking_confirmation(request):
    return render(request, "railway/booking_confirmation.html")


def train_route(request,train_id):
    # train=Train.objects.filter(id=train_id)
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


@login_required(login_url='/login/')
def passenger_details(request):
    booking_data = request.session.get('booking_data')
    if not booking_data:
        messages.error(request, "No booking data found.")
        return redirect('home')

    if request.method == 'POST':
        names = request.POST.getlist('name[]')
        ages = request.POST.getlist('age[]')
        genders = request.POST.getlist('gender[]')

        num_passengers = len(names)

        train = Train.objects.get(id=booking_data['train_id'])

        # ✅ Check seat availability
        total_booked = Booking.objects.filter(
            train=train,
            journey_date=booking_data['travel_date']
        ) .aggregate(Sum('seats_booked'))['seats_booked__sum'] or 0


        # .aggregate(models.Sum('seats_booked'))['seats_booked__sum'] or 0
        print("total_seats type:", type(total_booked))
        print(total_booked)
        # print("segment_data type:", type(segment_data))
        # booked_seats=total_booked['seats__sum']
        # available_seats = train.total_seats - booked_seats
        available_seats=train.total_seats-total_booked

        if num_passengers > available_seats:
            messages.error(request, f"Only {available_seats} seats available!")
            return render(request, 'passenger_details.html')

        # ✅ Save booking
        Booking.objects.create(
            user=request.user,
            train=train,
            from_station=booking_data['from_station'],
            to_station=booking_data['to_station'],
            journey_date=booking_data['travel_date'],
            seats_booked=num_passengers
        )

        messages.success(request, "Booking successful!")
        return redirect('home')

    return render(request, 'railway/passenger_details.html')

@login_required(login_url='/login/')
def enter_passenger_details(request):
    if request.method == 'POST':
        names = request.POST.getlist('name[]')
        ages = request.POST.getlist('age[]')
        genders = request.POST.getlist('gender[]')

        train_id = request.session.get('train_id')
        travel_date = request.session.get('travel_date')
        from_station = request.session.get('from_station')
        to_station = request.session.get('to_station')

        train = Train.objects.get(id=train_id)
        travel_date = parse_date(travel_date)

        for name, age, gender in zip(names, ages, genders):
            Passenger.objects.create(
                user=request.user,
                train=train,
                name=name,
                age=int(age),
                gender=gender,
                travel_date=travel_date,
                from_station=from_station,
                to_station=to_station
            )

        return redirect('print_ticket')  # Redirect to print ticket

    return render(request, 'enter_passenger_details.html')

@login_required(login_url='/login/')
def print_ticket(request):
    train_id = request.session.get('train_id')
    travel_date = request.session.get('travel_date')

    passengers = Passenger.objects.filter(
        user=request.user,
        train_id=train_id,
        travel_date=travel_date
    )

    return render(request, 'print_ticket.html', {'passengers': passengers})

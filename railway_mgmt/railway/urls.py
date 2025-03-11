from django.urls import path
from .views import (home, user_login, user_logout, book_ticket,
                    generate_otp, search_trains, register, send_otp, verify_otp, get_csrf_token,
                    booking_confirmation, train_route)

urlpatterns = [
    path('', home, name='home'),  # Home page
    path('register/',register, name='register'),
    path('login/', user_login, name='login'),  # Login page
    path('search_trains/', search_trains, name='search_trains'),
    path('send-otp/', send_otp, name='send_otp'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('logout/', user_logout, name='logout'),  # Logout functionality
    path('register/', register, name='register'),  # Registration page
    path('search/', search_trains, name='search_trains'),  # Train search API
    path('book/', book_ticket, name='book_ticket'),  # Train booking API
    path('booking-confirmation/', booking_confirmation, name='booking_confirmation'),
    path('generate-otp/', generate_otp, name='generate_otp'),  # OTP generation API
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('train-route/<int:train_id>/', train_route, name='train_route'),
    # path('confirm-booking/', confirm_booking, name='confirm_booking')

]

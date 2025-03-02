# 🚆 Railway Management System

A web-based **Railway Management System** built using **Django** and **MySQL**, allowing users to **search for trains, book tickets, and manage railway operations** efficiently.

## 📌 **Key Features**
- 🔍 **Train Search** - Find direct and intermediate trains between two stations.
- 🎟️ **Ticket Booking** - Users can book train tickets based on availability.
- 📅 **Train Schedule Management** - Manage running days and intermediate stations.
- 🔐 **User Authentication** - Secure login, registration, and logout functionality.
- 📧 **OTP-based Email Verification** - Users verify their email via OTP.
- 📊 **Admin Panel** - Manage trains, stations, and bookings via Django Admin.

---

## 🛠️ **Tech Stack**
- **Backend:** Django, Python
- **Database:** MySQL
- **Frontend:** HTML, CSS, JavaScript
- **Authentication:** Django’s built-in user model
- **Deployment:** Localhost (for now)

---

## ⚙️ **Installation & Setup**
### 🔹 **1. Clone the Repository**
```sh
git clone https://github.com/yourusername/railway-management-system.git
cd railway-management-system
```

### 🔹 **2. Create a Virtual Environment**
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
### 🔹 **3. Configure Database**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'railway_db',
        'USER': 'your_mysql_user',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
     }
}
```
### 🔹 **4. Run Migrations**
```sh
python manage.py makemigrations
python manage.py migrate
```
### 🔹 **5.  Create Superuser (for Admin Panel)**
```sh
python manage.py createsuperuser
```
### 🔹 **6.   Start the Server**
```sh
python manage.py runserver
```
Open the browser and visit: http://127.0.0.1:8000/

## **🚀 How to Use**
- 🏠 **1. Home Page** - Enter Source Station, Destination, and Date to search for available trains.

- 🔍 **2. Search Trains** - Displays direct trains and trains with intermediate stations.Users can click "Book Now" to reserve a seat.
- 🎟️ **3. Booking Tickets** - After logging in, users can select a train and book tickets.Available seats are updated dynamically.
- 🔐 **4. Authentication** - New users can Register and Login securely.OTP verification is used for added security.
- 🛠 **5. Admin Panel** - Superuser can add, edit, or delete trains, stations and bookings.Access it via: http://127.0.0.1:8000/admin/.

## **📂 Project Structure**
```sh
railway-management-system/
│── railway_mgmt/                  # Main Django project folder
│   ├── railway/                    # Django app for railway operations
│   │   ├── migrations/             # Database migrations
│   │   ├── templates/              # HTML templates
│   │   ├── static/                 # CSS & JavaScript files
│   │   ├── models.py               # Database models
│   │   ├── views.py                # Business logic
│   │   ├── urls.py                 # URL routing
│   │   ├── admin.py                # Django Admin configuration
│   │   ├── forms.py                # Django forms
│   ├── manage.py                   # Django management script
│── db.sqlite3                       # SQLite database (for development)
│── requirements.txt                  # Dependencies list
│── README.md                        # Project Documentation

```
## **🛠 Future Enhancements**
- 🏆 **Payment Integration** - Enable ticket booking with online payment.
- 🚆 **Real-time Seat Availability** - Show available seats dynamically.
- 📲 **Mobile-Friendly UI** - Improve responsiveness for mobile users.

## **🤝 Contributing**
**Contributions are welcome! If you find a bug or have a feature request, feel free to:**

- **1** Fork this repository.
- **2** Create a branch (git checkout -b feature-new-feature).
- **3** Commit your changes (git commit -m "Add new feature").
- **4** Push to the branch (git push origin feature-new-feature).
- **5** Create a Pull Request.

## **📞 Contact**

- **📧 Email:** lohi1734@gmail.com
- **🔗 GitHub:** [yourgithub](https://github.com/lo1734)
- **🔗 LinkedIn:** [yourlinkedin](https://www.linkedin.com/in/lohitaksha-n-949363262/)


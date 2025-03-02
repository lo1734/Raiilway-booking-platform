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

## ⚙️ **Installation & Setup**
### 🔹 **2. Create a Virtual Environment**
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

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

### 🔹 **4. Run Migrations**
```sh
python manage.py makemigrations
python manage.py migrate

### 🔹 **5.  Create Superuser (for Admin Panel)**
```sh
python manage.py createsuperuser

### 🔹 **6.   Start the Server**
```sh
python manage.py runserver

Open the browser and visit: http://127.0.0.1:8000/




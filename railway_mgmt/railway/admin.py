from django.contrib import admin
from django import forms
from .models import Train, IntermediateStation, CustomUser
from django.contrib.auth.admin import UserAdmin

# ✅ Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_staff", "is_active", "date_joined")

    fieldsets = (
        ("Personal Info", {"fields": ("username", "email", "password", "first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        ("Create User", {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "is_active", "is_staff"),
        }),
    )


# ✅ Train Admin Form (With "All Days" Checkbox)
class TrainAdminForm(forms.ModelForm):
    all_days = forms.BooleanField(required=False, label="All Days")

    class Meta:
        model = Train
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

        # ✅ Add checkboxes for each day
        for day in self.days:
            self.fields[day] = forms.BooleanField(required=False, label=day.capitalize())

        if self.instance and self.instance.pk:
            selected_days = [day for day in self.days if getattr(self.instance, day)]
            if len(selected_days) == 7:
                self.fields["all_days"].initial = True

    def clean(self):
        cleaned_data = super().clean()
        all_days_checked = cleaned_data.get("all_days", False)

        # ✅ If "All Days" is checked, mark all weekdays as True
        if all_days_checked:
            for day in self.days:
                cleaned_data[day] = True
        else:
            selected_days = [day for day in self.days if cleaned_data.get(day, False)]
            if len(selected_days) < 7:
                cleaned_data["all_days"] = False  # ✅ Uncheck "All Days" if any day is unchecked

        return cleaned_data


# ✅ Inline Intermediate Stations (Tabular View in Admin)
class IntermediateStationInline(admin.TabularInline):
    model = IntermediateStation
    extra = 1


# ✅ Train Admin (With Auto Insert for Intermediate Stations)
class TrainAdmin(admin.ModelAdmin):
    form = TrainAdminForm
    inlines = [IntermediateStationInline]
    list_display = ("train_number", "train_name", "source", "destination", "get_display_days")
    search_fields = ("train_number", "train_name", "source", "destination")

    fieldsets = (
        ("Train Details", {"fields": ("train_number", "train_name", "source", "destination", "total_seats")}),
        ("Timings", {"fields": ("boarding_time", "departure_time")}),
        ("Running Days", {
            "fields": ("all_days", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"),
            "classes": ("wide",),  # ✅ Display checkboxes horizontally
        }),
    )

    def get_display_days(self, obj):
        """Display selected running days in Django Admin."""
        selected_days = [day.capitalize() for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"] if getattr(obj, day)]
        return ", ".join(selected_days) if selected_days else "Not Set"

    get_display_days.short_description = "Operating Days"

    def save_model(self, request, obj, form, change):
        """
        ✅ Auto-add Source & Destination as Intermediate Stations.
        """
        super().save_model(request, obj, form, change)

        # ✅ Ensure the source is added as an intermediate station
        IntermediateStation.objects.get_or_create(
            train=obj,
            station_name=obj.source,
            arrival_time=obj.boarding_time,
            departure_time=obj.boarding_time,
        )

        # ✅ Ensure the destination is added as an intermediate station
        IntermediateStation.objects.get_or_create(
            train=obj,
            station_name=obj.destination,
            arrival_time=obj.departure_time,
            departure_time=obj.departure_time,
        )


# ✅ Register Models in Django Admin
admin.site.register(Train, TrainAdmin)
admin.site.register(CustomUser, CustomUserAdmin)

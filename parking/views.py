from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import Parking, Vehicle
from .forms import VehicleForm


def home(request):
    parking = Parking.objects.first()

    if parking:
        vehicles_inside = Vehicle.objects.filter(parking=parking, is_inside=True).count()
        free_spaces = parking.total_spaces - vehicles_inside
        revenue_today = Vehicle.objects.filter(
            parking=parking,
            is_inside=False
        ).aggregate(Sum("fee"))["fee__sum"] or 0
    else:
        vehicles_inside = 0
        free_spaces = 0
        revenue_today = 0

    context = {
        "free_spaces": free_spaces,
        "vehicles_inside": vehicles_inside,
        "revenue_today": revenue_today,
        "parking": parking,
    }

    return render(request, "parking/home.html", context)


def dashboard(request):
    parking = Parking.objects.first()

    if parking:
        vehicles_inside = Vehicle.objects.filter(parking=parking, is_inside=True).count()
        free_spaces = parking.total_spaces - vehicles_inside
        revenue_today = Vehicle.objects.filter(
            parking=parking,
            is_inside=False
        ).aggregate(Sum("fee"))["fee__sum"] or 0
        vehicles = Vehicle.objects.filter(parking=parking).order_by("-entry_time")
    else:
        vehicles_inside = 0
        free_spaces = 0
        revenue_today = 0
        vehicles = []

    context = {
        "parking": parking,
        "vehicles_inside": vehicles_inside,
        "free_spaces": free_spaces,
        "revenue_today": revenue_today,
        "vehicles": vehicles,
    }

    return render(request, "parking/dashboard.html", context)


def enter_vehicle(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = VehicleForm()

    context = {
        "form": form
    }

    return render(request, "parking/enter_vehicle.html", context)
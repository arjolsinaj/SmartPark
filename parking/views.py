from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal

from .models import Parking, Vehicle
from .forms import VehicleForm


def home(request):
    parking = Parking.objects.first()

    if parking:
        vehicles_inside = Vehicle.objects.filter(parking=parking, is_inside=True).count()
        free_spaces = max(parking.total_spaces - vehicles_inside, 0)

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
        free_spaces = max(parking.total_spaces - vehicles_inside, 0)

        revenue_today = Vehicle.objects.filter(
            parking=parking,
            is_inside=False
        ).aggregate(Sum("fee"))["fee__sum"] or 0

        search_query = request.GET.get("search", "")
        status_filter = request.GET.get("status", "all")

        vehicles = Vehicle.objects.filter(parking=parking)

        if search_query:
            vehicles = vehicles.filter(plate_number__icontains=search_query)

        if status_filter == "inside":
            vehicles = vehicles.filter(is_inside=True)

        elif status_filter == "exited":
            vehicles = vehicles.filter(is_inside=False)

        vehicles = vehicles.order_by("-entry_time")

    else:
        vehicles_inside = 0
        free_spaces = 0
        revenue_today = 0
        vehicles = []
        search_query = ""
        status_filter = "all"

    context = {
        "parking": parking,
        "vehicles_inside": vehicles_inside,
        "free_spaces": free_spaces,
        "revenue_today": revenue_today,
        "vehicles": vehicles,
        "search_query": search_query,
        "status_filter": status_filter,
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


def exit_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    vehicle.exit_time = timezone.now()
    vehicle.is_inside = False

    duration = vehicle.exit_time - vehicle.entry_time
    hours = Decimal(duration.total_seconds() / 3600)

    if hours < 1:
        hours = Decimal(1)

    vehicle.fee = hours * vehicle.parking.price_per_hour
    vehicle.save()

    return redirect("dashboard")


def vehicle_detail(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    context = {
        "vehicle": vehicle
    }

    return render(request, "parking/vehicle_detail.html", context)
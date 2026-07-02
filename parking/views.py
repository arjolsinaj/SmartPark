from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.core.paginator import Paginator
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
        today = timezone.now().date()

        vehicles_inside = Vehicle.objects.filter(parking=parking, is_inside=True).count()
        free_spaces = max(parking.total_spaces - vehicles_inside, 0)

        revenue_today = Vehicle.objects.filter(
            parking=parking,
            is_inside=False
        ).aggregate(Sum("fee"))["fee__sum"] or 0

        total_vehicles = Vehicle.objects.filter(parking=parking).count()

        entries_today = Vehicle.objects.filter(
            parking=parking,
            entry_time__date=today
        ).count()

        exits_today = Vehicle.objects.filter(
            parking=parking,
            exit_time__date=today
        ).count()

        average_fee = Vehicle.objects.filter(
            parking=parking,
            is_inside=False
        ).aggregate(Avg("fee"))["fee__avg"] or 0

        if parking.total_spaces > 0:
            occupancy_rate = round((vehicles_inside / parking.total_spaces) * 100, 2)
        else:
            occupancy_rate = 0

        search_query = request.GET.get("search", "")
        status_filter = request.GET.get("status", "all")
        start_date = request.GET.get("start_date", "")
        end_date = request.GET.get("end_date", "")

        vehicles = Vehicle.objects.filter(parking=parking)

        if search_query:
            vehicles = vehicles.filter(plate_number__icontains=search_query)

        if status_filter == "inside":
            vehicles = vehicles.filter(is_inside=True)
        elif status_filter == "exited":
            vehicles = vehicles.filter(is_inside=False)

        if start_date:
            vehicles = vehicles.filter(entry_time__date__gte=start_date)

        if end_date:
            vehicles = vehicles.filter(entry_time__date__lte=end_date)

        vehicles = vehicles.order_by("-entry_time")

        paginator = Paginator(vehicles, 5)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        revenue_data = (
            Vehicle.objects
            .filter(parking=parking, is_inside=False)
            .annotate(day=TruncDate("exit_time"))
            .values("day")
            .annotate(total=Sum("fee"))
            .order_by("day")
        )

        chart_labels = []
        chart_values = []

        for item in revenue_data:
            if item["day"]:
                chart_labels.append(item["day"].strftime("%Y-%m-%d"))
                chart_values.append(float(item["total"] or 0))

    else:
        vehicles_inside = 0
        free_spaces = 0
        revenue_today = 0
        total_vehicles = 0
        entries_today = 0
        exits_today = 0
        average_fee = 0
        occupancy_rate = 0
        search_query = ""
        status_filter = "all"
        start_date = ""
        end_date = ""
        page_obj = []
        chart_labels = []
        chart_values = []

    context = {
        "parking": parking,
        "vehicles_inside": vehicles_inside,
        "free_spaces": free_spaces,
        "revenue_today": revenue_today,
        "total_vehicles": total_vehicles,
        "entries_today": entries_today,
        "exits_today": exits_today,
        "average_fee": average_fee,
        "occupancy_rate": occupancy_rate,
        "vehicles": page_obj,
        "page_obj": page_obj,
        "search_query": search_query,
        "status_filter": status_filter,
        "start_date": start_date,
        "end_date": end_date,
        "chart_labels": chart_labels,
        "chart_values": chart_values,
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
from django.shortcuts import render
from django.db.models import Sum
from .models import Parking, Vehicle


def home(request):
    parking = Parking.objects.first()

    if parking:
        vehicles_inside = Vehicle.objects.filter(
            parking=parking,
            is_inside=True
        ).count()

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
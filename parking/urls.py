from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("enter-vehicle/", views.enter_vehicle, name="enter_vehicle"),
    path("exit-vehicle/<int:vehicle_id>/", views.exit_vehicle, name="exit_vehicle"),

    path(
        "vehicle/<int:vehicle_id>/",
        views.vehicle_detail,
        name="vehicle_detail"
    ),
]
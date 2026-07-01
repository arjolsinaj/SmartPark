from django import forms
from .models import Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["parking", "plate_number"]

    def clean(self):
        cleaned_data = super().clean()

        parking = cleaned_data.get("parking")
        plate_number = cleaned_data.get("plate_number")

        if parking:
            vehicles_inside = Vehicle.objects.filter(
                parking=parking,
                is_inside=True
            ).count()

            if vehicles_inside >= parking.total_spaces:
                raise forms.ValidationError(
                    "Parking is full. No free spaces available."
                )

        if parking and plate_number:
            if Vehicle.objects.filter(
                parking=parking,
                plate_number=plate_number,
                is_inside=True
            ).exists():
                raise forms.ValidationError(
                    "This vehicle is already inside this parking."
                )

        return cleaned_data
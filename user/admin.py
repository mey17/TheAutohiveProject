from django.contrib import admin
from .models import ParkingPlace, Slot

class ParkingPlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'unique_id', 'max_slots', 'reserved_slots', 'is_active')
    search_fields = ('name', 'address', 'unique_id')
    list_filter = ('is_active',)

admin.site.register(ParkingPlace, ParkingPlaceAdmin)
admin.site.register(Slot)

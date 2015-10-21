from django.contrib import admin
from .models import OilType, SeedData

# Register your models here.

admin.site.register(SeedData)
admin.site.register(OilType)
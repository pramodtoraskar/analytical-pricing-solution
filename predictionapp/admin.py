from django.contrib import admin
from .models import OilType, SeedData, SourceKey, OilDescSourceKeyMapping

# Register your models here.

admin.site.register(SeedData)
admin.site.register(OilType)
admin.site.register(SourceKey)
admin.site.register(OilDescSourceKeyMapping)

from django.contrib import admin
from .models import OilType, SeedData, SourceKey, OilDescSourceKeyMapping, \
    OilProductionByMonthBySingleCol, OilProductionByMonthByTwoCol, \
    OilProductionByMonthByMulCol

# Register your models here.

admin.site.register(SeedData)
admin.site.register(OilType)
admin.site.register(SourceKey)
admin.site.register(OilDescSourceKeyMapping)
admin.site.register(OilProductionByMonthBySingleCol)
admin.site.register(OilProductionByMonthByTwoCol)
admin.site.register(OilProductionByMonthByMulCol)
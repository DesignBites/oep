from django.contrib import admin
from oep.network.models import Map, Sector, Purpose, RelationType


@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_own', 'sector', 'size']


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Purpose)
class PurposeAdmin(admin.ModelAdmin):
    list_display = ['description']


@admin.register(RelationType)
class RelationTypeAdmin(admin.ModelAdmin):
    list_display = ['group', 'name', 'order']
    list_editable = ['order']

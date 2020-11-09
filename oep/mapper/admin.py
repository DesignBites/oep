from io import BytesIO
import qrcode
import qrcode.image.svg
import csv
from slugify import slugify
from django.http import HttpResponse
from django.conf import settings
from django.contrib import admin
from .models import Map, Sector, Purpose, RelationType, Workshop


@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_own', 'sector', 'size']
    actions = ['download']

    def download(selfself, queryset):
        for m in queryset:
            pass


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Purpose)
class PurposeAdmin(admin.ModelAdmin):
    list_display = ['description']


@admin.register(RelationType)
class RelationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}
    actions = ['get_qr']

    def get_qr(self, request, queryset):
        factory = qrcode.image.svg.SvgFragmentImage
        for workshop in queryset:
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=6,
                border=1,
                image_factory=factory,
            )
            qr.add_data(
                '%s%s' % (
                    settings.BASE_SITE_URL,
                    workshop.get_absolute_url(),
                 )
            )
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img_buffer = BytesIO()
            img.save(img_buffer)
            img_buffer.seek(0)
            response = HttpResponse(
                img_buffer.read(),
                content_type='image/svg+xml',
            )
            response['Content-Disposition'] = 'attachment; filename="QR-%s.svg"' % slugify(workshop.slug[:20])
            break
        return response
    get_qr.short_description = 'Get QR code'

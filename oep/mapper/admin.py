import csv
from io import BytesIO, StringIO
import qrcode
import qrcode.image.svg
from slugify import slugify
from django.http import HttpResponse
from django.conf import settings
from django.contrib import admin
from django.forms import ModelForm
from trumbowyg.widgets import TrumbowygWidget
from .models import Map, Sector, StakeholderType, Workshop, PageInfo


@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    list_display = ['name', 'workshop', 'created', 'modified', 'is_own', 'sector', 'size']
    actions = ['download']

    def download(self, request, qs):
        f = StringIO()
        writer = csv.writer(f)
        for m in qs:
            writer.writerow([
                'Name',
                'Batch',
                'Value similarity',
                'Way of working similarity',
                'Resources similarity',
                m.own_parameter or 'Own parameter (not specified)',
                'Interaction frequency',
                'Collaboration frequency',
            ])
            stakeholders = m.stakeholders or {}
            for name, data in stakeholders.items():
                writer.writerow([
                    name,
                    ', '.join(data.get('types', [])),
                    'values' in data.get('similarities', []) and 'Yes' or 'No',
                    'working' in data.get('similarities', []) and 'Yes' or 'No',
                    'resources' in data.get('similarities', []) and 'Yes' or 'No',
                    'custom' in data.get('similarities', []) and 'Yes' or 'No',
                    data.get('interact', ''),
                    data.get('collaborate', ''),
                ])
            f.seek(0)
            response = HttpResponse(
                f.read(),
                content_type='text/csv'
            )
            response['Content-Disposition'] = 'attachment; filename="%s-stakeholders.csv"' % m.name
            return response
    download.short_description = 'Download stakeholders (CSV)'


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(StakeholderType)
class StakeholderTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'batch_no', 'order']
    list_editable = ['batch_no', 'order']


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


class PageInfoModelAdminForm(ModelForm):
    class Meta:
        model = PageInfo
        fields = ['page', 'title', 'description']
        widgets = {
            'description': TrumbowygWidget(),
        }


@admin.register(PageInfo)
class PageInfoAdmin(admin.ModelAdmin):
    list_display = ['page', 'title', 'description']
    list_editable = ['title']
    form = PageInfoModelAdminForm

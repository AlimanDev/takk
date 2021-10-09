from django.contrib import admin
from apps.companies import models
# Register your models here.


@admin.register(models.Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_activate', 'created_dt', 'updated_dt')
    list_filter = ('created_dt', 'updated_dt', 'is_activate')
    search_fields = ('name', )


@admin.register(models.Cafe)
class CafeAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'company', 'menu', 'created_dt')
    list_filter = ('created_dt', 'updated_dt', 'status')
    search_fields = ('name', 'company__name', 'company__id')



@admin.register(models.CafeWeekTime)
class CafeWeekTimeAdmin(admin.ModelAdmin):
    list_display = ('cafe', 'day', 'is_open', 'opening_time', 'closing_time')
    search_fields = ('cafe__name', 'cafe__id')
    list_display_links = ('cafe',)


@admin.register(models.Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    search_fields = ('name', 'company__name', 'company__id')


@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'employee_position')
    list_filter = ('employee_position', )
    search_fields = ('user', 'user__id', 'company__name', 'company__id')
    list_display_links = ('company', 'user')


@admin.register(models.CafePhoto)
class CafePhotoAdmin(admin.ModelAdmin):
    list_display = ('cafe', )
    search_fields = ('cafe', 'cafe__id')
    list_display_links = ('cafe', )


@admin.register(models.TakkFeeForCompany)
class TakkFeeForCompanyAdmin(admin.ModelAdmin):
    list_display = ('company', 'is_percent', 'fee_percent', 'fee_amount')
    list_filter = ('is_percent',)
    search_fields = ('company__name', 'company__id')
    list_display_links = ('company',)


@admin.register(models.CompanyCard)
class CompanyCardAdmin(admin.ModelAdmin):
    list_display = ('company', 'account_id', 'name', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('company__name', 'company__id')
    list_display_links = ('company',)


@admin.register(models.TakkGeneralSettings)
class TakkGeneralSettingsAdmin(admin.ModelAdmin):
    pass



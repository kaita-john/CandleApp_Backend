from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AppUser

# Register your models here.
from django.contrib import admin

class AppUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'is_active', 'is_celeb', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    list_filter = ('is_active', 'is_celeb', 'is_staff')
    fieldsets = (
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'gender', 'location', 'stagename', 'tagline', 'biotext', 'image'),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_admin', 'is_celeb', 'roles', 'groups'),
        }),
        ('Password', {
            'fields': ('password',),
        }),
    )

admin.site.register(AppUser, AppUserAdmin)

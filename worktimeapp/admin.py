from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm
from django.contrib.auth import get_user_model
User = get_user_model()


class CustomUserAdmin(UserAdmin):
    form = CustomUserCreationForm
    model = CustomUser
    list_display = ['id', 'email', 'first_name', 'last_name', 'organization', 'is_superuser']
    list_filter = ['is_superuser']
    ordering = ('email',)
    list_display_links = ['email']


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'email']
    list_display_links = ['title']
    search_fields = ['title', 'email']
    list_filter = ['title']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Time)

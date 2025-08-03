from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import CustomerProfile, ProviderProfile, PhoneOTP


class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = 'Customer Profile'
    
# Customize User display in admin
class CustomUserAdmin(BaseUserAdmin):
    inlines = [CustomerProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name','get_phone_number', 'is_staff')
    search_fields = ('username', 'email')

    def get_phone_number(self, obj):
        return obj.customerprofile.phone_number if hasattr(obj, 'customerprofile') else "-"
    get_phone_number.short_description = 'Phone Number'

# Remove default User admin and re-register
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Customize CustomerProfile admin
@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'get_full_name', 'phone_number')
    search_fields = ('user__username', 'user__email', 'phone_number')

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Full Name'


@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'business_name', 'categories', 'location', 'status')
    search_fields = ('user__username', 'phone', 'business_name', 'location', 'categories')
    list_filter = ('status',)


# --- PhoneOTP Admin ---
@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'otp', 'is_verified', 'timestamp')
    search_fields = ('phone_number',)
    list_filter = ('is_verified',)


# Register ProviderProfile normally
# admin.site.register(ProviderProfile)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type')
    list_filter = ('is_staff', 'is_superuser', 'userprofile__user_type')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'userprofile__phone_number')

    def get_user_type(self, obj):
        return obj.userprofile.get_user_type_display()
    get_user_type.short_description = 'User Type'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'phone_number', 'vehicle_type', 'created_at')
    list_filter = ('user_type', 'vehicle_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number', 'address')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'first_name', 'last_name', 'phone_number', 'address')
        }),
        ('Role Information', {
            'fields': ('user_type', 'vehicle_type')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

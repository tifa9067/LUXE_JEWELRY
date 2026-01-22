from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'الملف الشخصي'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__user_type')
    
    def get_user_type(self, obj):
        return obj.profile.get_user_type_display()
    get_user_type.short_description = 'نوع المستخدم'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)
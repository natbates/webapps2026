from django.contrib import admin
from django.contrib.auth import get_user_model

# Note: The coursework requires you to implement admin functionality via views,
# not to rely on Django's admin site. The registration below is provided for
# convenience when developing locally — you may ignore it for marking.

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'currency', 'balance')
    search_fields = ('username', 'email')

from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Subscribe


User = get_user_model()

admin.site.register(Subscribe)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
    )
    list_filter = ('email', 'username')
    search_fields = ('username', 'email',)

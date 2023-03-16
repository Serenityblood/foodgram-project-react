from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username',
        'first_name', 'last_name',
        'email', 'recipes', 'password'
    )
    list_editable = (
        'password', 'username', 'first_name', 'last_name', 'email'
    )
    search_fields = ('username',)
    list_filter = ('username', 'email')
    empty_value_display = '--пусто--'

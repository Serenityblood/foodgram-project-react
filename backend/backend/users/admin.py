from django.contrib import admin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'get_subscribers_count', 'get_favorite_count', 'email'
    )
    list_filter = ('email', 'username')
    search_fields = ('username', 'email',)

    def get_subscribers_count(self, obj):
        return obj.subscribing.count()

    def get_favorite_count(self, obj):
        return obj.favorite_set.count()


admin.site.register(Subscribe)

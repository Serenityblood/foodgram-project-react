from django.urls import include, path


urlpatterns = [
    path('', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken'))
]
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tools.urls')),  # replace 'tools' with your app folder name
]

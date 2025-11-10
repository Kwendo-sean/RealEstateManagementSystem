from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # User authentication URLs (login, register, etc.)
    path('users/', include('users.urls')),

    # M-Pesa payments URLs
    path('payments/', include('payments.urls')),
]

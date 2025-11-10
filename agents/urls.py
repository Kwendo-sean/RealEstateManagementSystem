from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Redirect root to login page
    path('', lambda request: redirect('login')),
    
    # Include user authentication URLs
    path('', include('users.urls')),
    
    # Include M-Pesa payments app URLs
    path('payments/', include('payments.urls')),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.agent_list, name='agent_list'),            # Agents page
    path('dashboard/', views.dashboard, name='dashboard'),    # Dashboard page
    path('properties/', views.properties, name='properties'),# Properties page
    path('clients/', views.clients, name='clients'),         # Clients page
]

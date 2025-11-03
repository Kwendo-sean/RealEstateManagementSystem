from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from users.models import Profile

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            role = user.profile.role  
           # Redirect based on roles
            if role == 'admin':
                return redirect('admin_dashboard')
            elif role == 'agent':
                return redirect('agent_dashboard')
            elif role == 'customer':
                return redirect('customer_dashboard')
            else:
                messages.error(request, "Invalid role assigned.")
                return redirect('login')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'users/login.html')
def admin_dashboard(request):
    return render(request, 'dashboards/admin_dashboard.html')

def agent_dashboard(request):
    return render(request, 'dashboards/agent_dashboard.html')

def customer_dashboard(request):
    return render(request, 'dashboards/customer_dashboard.html')
from django.shortcuts import render, redirect
from .models import Agent
from .forms import AgentForm
from django.shortcuts import render

def clients(request):
    return render(request, 'clients.html')

def dashboard(request):
    return render(request, 'dashboard.html')  # Make sure dashboard.html exists
def properties(request):
    return render(request, 'properties.html') 

def agent_list(request):
    agents = Agent.objects.all()

    if request.method == 'POST':
        form = AgentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('agent_list')
    else:
        form = AgentForm()

    return render(request, 'agents.html', {'agents': agents, 'form': form})

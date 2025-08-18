from django.shortcuts import render
from missions.models import Mission

def main(request):
    return render(request, 'home/main.html')

from ai_services.services import store_recommend
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def main(request):
    recommended_stores = store_recommend(request.user)
    return render(request, "home/main.html", {"recommended_stores": recommended_stores})
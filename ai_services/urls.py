from django.urls import path
from . import views

app_name = "ai_services"

urlpatterns = [
    path('review-summary/<int:store_id>/', views.review_summary, name='review_summary'),
]

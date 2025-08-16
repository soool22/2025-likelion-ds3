from django.urls import path
from . import views

app_name = "visit_rewards"

urlpatterns = [
  
    path('visit_check/<int:store_id>/', views.visit_check, name='visit_check'),# QR 인증 화면
    path('visit/', views.visit_store, name='visit_store'),  # QR 스캔 후 API
]

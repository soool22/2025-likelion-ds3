from django.urls import path
from .views import *

app_name="reviews"

urlpatterns = [
    path('review-create/<int:store_id>/', review_create, name='review-create'),
    path('review-list/<int:store_id>/', review_list, name='review-list'),
    path('review-delete/<int:review_id>/', review_delete, name='review-delete'),
]
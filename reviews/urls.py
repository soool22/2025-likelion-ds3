from django.urls import path
from .views import *

app_name="reviews"

urlpatterns = [
    path('review-create/<int:store_id>/', review_create, name='review-create'),
    path('review-list/<int:store_id>/', review_list, name='review-list'),
    path('review-delete/<int:review_id>/', review_delete, name='review-delete'),
    path('review-like-toggle/<int:review_id>/', review_like_toggle, name='review-like-toggle'),
    path('my-review/', my_review, name='my-review'),

    path('owner-review-list/<int:store_id>/', owner_review_list, name='owner-review-list'), # 점주용
]
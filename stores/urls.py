from django.urls import path
from .views import *

app_name="stores"

urlpatterns = [
    path('store-create/', store_create, name='store-create'),
    path("store-location/", store_location, name="store-location"),
    path('owner-store-list/', owner_store_list, name='owner-store-list'), # 점주용
    path('store-delete/<int:store_id>/', store_delete, name='store-delete'),
    path('store-update/<int:store_id>/', store_update, name='store-update'),

    path('', public_store_list, name='public-store-list'),  # 전체 가게 목록
    path('popular-store-list/',popular_store_list,name='popular-store-list'),
    path('review-best-list/', review_best_list, name='review-best-list'),
    path('store-detail/<int:store_id>', store_detail, name='store-detail'),
    path('store-search/', store_search, name='store-search'),
]
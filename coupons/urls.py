from django.urls import path
from . import views

app_name = "coupons"

urlpatterns = [
    path('use-coupons/', views.use_coupon, name='use_coupon'),
    path('create-coupons/', views.create_coupon, name='create_coupon'),
    path('create-coupons/<int:store_id>/', views.create_coupon, name='create_coupon_store'),
    
        # 가게별 쿠폰 목록
    path('store/<int:store_id>/coupons/', views.coupon_list, name='coupon_list'),

    # 개별 쿠폰 수정/삭제
    path('update/<int:coupon_id>/', views.update_coupon, name='update_coupon'),
    path('delete/<int:coupon_id>/', views.delete_coupon, name='delete_coupon'),

]

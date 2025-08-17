from django.urls import path
from . import views

app_name = "visit_rewards"

urlpatterns = [
    # 방문 관련
    path('visit_check/<int:store_id>/', views.visit_check, name='visit_check'),  # QR 인증 화면
    path('visit/', views.visit_store, name='visit_store'),                        # QR 스캔 후 API

    # 내 보유 포인트/아이템/기프티콘
    path('rewards/', views.my_rewards, name='my_rewards'),

    # 꾸미기 아이템 관련
    path('shop/items/', views.shop_items, name='shop_items'),                     # 아이템 샵
    path('shop/items/buy/<int:item_id>/', views.buy_item, name='buy_item'),      # 아이템 구매

    # 기프티콘 관련
    path('shop/gifticons/', views.shop_gifticons, name='shop_gifticons'),        # 기프티콘 샵
    path('shop/gifticons/buy/<int:gifticon_id>/', views.buy_gifticon, name='buy_gifticon'),  # 기프티콘 구매
    path('gifticons/my/', views.my_gifticons, name='my_gifticons'),              # 보유 기프티콘 확인
    path('gifticons/use/', views.use_gifticon, name='use_gifticon'),
    
    # 구매 내역
    path('gifticons/purchase-history/', views.purchase_history, name='purchase_history'),
]

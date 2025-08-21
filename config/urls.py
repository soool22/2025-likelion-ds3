from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from visit_rewards import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.full_urls')),  # 커스텀 + 소셜 로그인 통합(루트 경로 처리)
    path('visit_rewards/', include('visit_rewards.urls')),
    path('home/',include('home.urls')), # home url
    path('stores/',include('stores.urls')), # stores url
    path('reviews/',include('reviews.urls')), # reviews url
    path('missions/',include('missions.urls')), # missions url
    path('products/',include('products.urls')), # products url
    path('ai/', include('ai_services.urls', namespace='ai_services')),
    path('coupons/', include('coupons.urls', namespace='coupons')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


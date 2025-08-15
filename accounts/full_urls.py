from django.urls import path, include

urlpatterns = [
    path('', include('accounts.urls')),      # 기존 내 로그인/회원가입/마이페이지 등
   # path('', include('allauth.urls')),       # 소셜 로그인 URL 대비
]

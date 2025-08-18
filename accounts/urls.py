from django.urls import path
from .views import *
from . import views

app_name="accounts"

urlpatterns = [
# 계정 API

path('', main_page_view, name='main'),  # 루트 경로 처리

path('signup/', signup, name='signup'),
path('login/', login, name='login'),
path('logout/', logout, name="logout"),
path('delete/', delete_account, name='delete_account'),
path('edit/', profile_edit, name='profile_edit'),
path('api/user/', user_info_view, name='user_info'),

path('visit_check/',visit_check,name='visit_check'),


path('page/mypage/', my_page_view, name='mypage'),
path('page/login/', login_page_view, name='login_page'),
path('page/signup/', signup_page_view, name='signup_page'),

path('terms/', lambda request: terms_or_policy_view(request, 'terms'), name='terms_of_service'),
path('privacy/', lambda request: terms_or_policy_view(request, 'privacy'), name='privacy_policy'),


path('preferences/', views.user_preferences, name='user_preferences'),
path('favorites/', views.favorite_stores, name='favorite_stores'),
path('favorites/toggle/', views.toggle_favorite, name='toggle_favorite'),

]
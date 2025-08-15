from django.urls import path
from .views import *

app_name="missions"

urlpatterns = [
    path('mission-list/<int:store_id>/', mission_list, name='mission-list'),
    path('mission-create/<int:store_id>/', mission_create, name='mission-create'),  
    path('mission-update/<int:mission_id>>/', mission_update, name='mission-update'), 
    path('mission-delete/<int:mission_id>>/', mission_delete, name='mission-delete'), 
    path('mission-complete/<int:mission_id>/', mission_complete, name='mission-complete'),
]
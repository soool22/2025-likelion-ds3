from django.contrib import admin
from .models import MissionType, Mission

# Register your models here.
admin.site.register(MissionType)
admin.site.register(Mission)
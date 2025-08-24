from math import radians, sin, cos, sqrt, atan2
from collections import defaultdict
from django.db.models import Count, Avg, F, FloatField, ExpressionWrapper
from accounts.models import UserLocation
from .models import Store

# 거리 계산
def haversine(lat1, lon1, lat2, lon2):
    """두 좌표 간 거리 계산 (m 단위)"""
    R = 6371  # km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance_m = R * c * 1000  # m 단위
    return distance_m  # 숫자 값만 반환

def format_distance(distance_m):
    """출력용 단위 변환"""
    if distance_m < 1000:
        return f"{int(distance_m)} m"
    else:
        return f"{distance_m/1000:.2f} km"

# 사용자 위치 가져오기
def get_user_location(user):
    try:
        loc = UserLocation.objects.get(user=user)
        return loc.latitude, loc.longitude, loc.gu_name
    except UserLocation.DoesNotExist:
        return 37.5665, 126.9780, "서울특별시"  # 기본값

# 거리 계산 후 Store 객체에 distance 속성 추가
def annotate_distance(stores, user_lat, user_lng):
    for store in stores:
        if store.latitude and store.longitude:
            distance_m = haversine(user_lat, user_lng, store.latitude, store.longitude)
            store.distance_m = distance_m       # 계산용 숫자
            store.distance = format_distance(distance_m)  # 출력용 문자열
        else:
            store.distance_m = None
            store.distance = None
    return stores

# 방문자 수 계산 (하루 최대 2회)
def calculate_visit_counts(stores, visits, category_slug=None):
    visit_counts = defaultdict(int)
    for v in visits:
        if category_slug and not v.store.category.filter(slug=category_slug).exists():
            continue
        key = (v.store_id, v.user_id)
        visit_counts[key] = min(visit_counts.get(key, 0) + 1, 2)

    total_counts = defaultdict(int)
    for (store_id, user_id), count in visit_counts.items():
        total_counts[store_id] += count

    for store in stores:
        store.visit_count = total_counts.get(store.id, 0)
    return stores

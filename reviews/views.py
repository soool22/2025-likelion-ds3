from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from datetime import timedelta
from django.utils import timezone
from .models import *
from stores.models import Store
from django.db.models import Count
from django.http import JsonResponse
from visit_rewards.models import Visit, Reward
from django.http import HttpResponse

@login_required
def review_create(request, store_id):
    store = get_object_or_404(Store, id=store_id)

    # 최근 24시간 방문 기록 가져오기
    time_threshold = timezone.now() - timedelta(hours=24)
    recent_visits = Visit.objects.filter(
        user=request.user,
        store=store,
        visit_time__gte=time_threshold
    )

    visit_count = recent_visits.count()

    if visit_count == 0:
        return HttpResponse("""
            <script>
                alert('최근 24시간 내 방문 인증 기록이 있어야 리뷰 작성이 가능합니다.');
                history.back();
            </script>
        """)

    # 이미 작성한 리뷰 수
    user_review_count = Review.objects.filter(
        user=request.user,
        store=store,
        created_at__gte=time_threshold
    ).count()

    if user_review_count >= visit_count:
        return HttpResponse(f"""
            <script>
                alert('리뷰는 방문 1회 당 1건만 작성할 수 있습니다.');
                history.back();
            </script>
        """)

    # POST 요청 처리
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '')
        images = request.FILES.getlist('images')

        if rating < 1 or rating > 5:
            return HttpResponse("""
                <script>
                    alert('별점은 1~5 사이여야 합니다.');
                    history.back();
                </script>
            """)

        review = Review.objects.create(
            store=store,
            user=request.user,
            rating=rating,
            comment=comment,
        )

        for image in images:
            ReviewImage.objects.create(review=review, image=image)

        store.update_rating()
        
        points_earned = 500
        Reward.objects.create(
            user=request.user,
            store=store,
            reward_type='point',
            related_review=review,
            amount=points_earned,
            description='리뷰 작성 보상'
        )

        request.user.points += points_earned
        request.user.save()

        return HttpResponse("""
            <script>
                alert('리뷰가 등록되었습니다.\n 500 point 적립 완료!');
                window.location.href = '/reviews/{store_id}/';  // 리뷰 목록으로 이동
            </script>
        """)

    return render(request, 'reviews/review-create.html', {'store': store})


# 리뷰 목록
@login_required
def review_list(request, store_id):
    store = get_object_or_404(Store, id=store_id)

    # 기본 QuerySet
    reviews = Review.objects.filter(store=store).prefetch_related('images').annotate(
        helpful_count=Count('likes')  # 좋아요 수 계산
    )

    # 정렬 파라미터
    sort = request.GET.get('sort', 'latest')  # 기본값 최신순
    if sort == 'latest':
        reviews = reviews.order_by('-created_at')
    elif sort == 'rating_desc':
        reviews = reviews.order_by('-rating')
    elif sort == 'rating_asc':
        reviews = reviews.order_by('rating')
    elif sort == 'helpful':
        reviews = reviews.order_by('-helpful_count')

    # 평균 평점 계산
    avg_rating = store.rating
    avg_star_count = int(round(avg_rating))

    # 별 리스트 1~5
    stars_list = range(1, 6)

    # 별점별 리뷰 개수 (1~5)
    rating_counts = {i: reviews.filter(rating=i).count() for i in range(1, 6)}

    # 각 리뷰에 별 표시 추가
    for review in reviews:
        review.stars = "★" * review.rating
        
    print("현재 시간:", timezone.now())
    print("최근 24시간 기준:", timezone.now() - timedelta(hours=24))
    print("최근 Visit:", Visit.objects.filter(user=request.user, store=store).values_list('visit_time', flat=True))


    # 방문 여부 체크 (최근 24시간 내 방문 기록)
    # 최근 24시간 방문 기록
    time_threshold = timezone.now() - timedelta(hours=24)

    # UTC 기준으로 DB에 저장된 visit_time과 비교
    has_recent_visit = Visit.objects.filter(
        user=request.user,
        store=store,
        visit_time__gte=time_threshold
    ).exists()


    return render(request, 'reviews/review-list.html', {
        'store': store,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'avg_star_count': avg_star_count,
        'stars_list': stars_list,
        'rating_counts': rating_counts,
        'sort': sort,
        'has_recent_visit': has_recent_visit,  # ✅ 템플릿으로 전달
    })

# 리뷰 삭제
@login_required
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.method == 'POST':
        store_id = review.store.id
        review.delete()
        messages.success(request, "리뷰가 삭제되었습니다.")
        return redirect('reviews:review-list', store_id=store_id)

    # 삭제 페이지에서도 별 표시
    review.stars = "★" * review.rating

    return render(request, 'reviews/review-delete.html', {'review': review})

# 리뷰 좋아요/취소 (도움이 돼요)
@login_required
def review_like_toggle(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    user = request.user

    # 자기 리뷰는 좋아요 불가
    if review.user == user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(status=400)
        return redirect('reviews:review-list', store_id=review.store.id)

    # 좋아요 
    if user in review.likes.all():
        review.likes.remove(user)
        liked = False
    else:
        review.likes.add(user)
        liked = True

    like_count = review.likes.count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'like_count': like_count})

    return redirect('reviews:review-list', store_id=review.store.id)

# 내가 작성한 리뷰
@login_required
def my_review(request):
    reviews = Review.objects.filter(user=request.user).prefetch_related('images').order_by('-created_at')

    # 별점 표시용
    for review in reviews:
        review.stars = "★" * review.rating

    return render(request, 'reviews/my-review.html', {
        'reviews': reviews,
    })
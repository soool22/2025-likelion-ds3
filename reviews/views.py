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

# 리뷰 작성 
@login_required
def review_create(request, store_id):
    store = get_object_or_404(Store, id=store_id)

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '')
        images = request.FILES.getlist('images')  # 다중 이미지 처리

        if rating < 1 or rating > 5:
            messages.error(request, "별점은 1~5 사이여야 합니다.")
            return redirect(request.path)

        review = Review.objects.create(
            store=store,
            user=request.user,
            rating=rating,
            comment=comment,
        )

        # 이미지 여러 개 저장
        for image in images:
            ReviewImage.objects.create(review=review, image=image)

        store.update_rating()  # 평균 평점 갱신
        messages.success(request, "리뷰가 등록되었습니다.")
        return redirect('reviews:review-list', store_id=store.id)

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

    now = timezone.now()  # 현재 시간

    # 각 리뷰에 별 표시 추가
    for review in reviews:
        review.stars = "★" * review.rating

        # 날짜 차이 계산
        delta = now - review.created_at
        days = delta.days
        review.natural_days = f"{days}일 전" if days > 0 else "오늘"

    return render(request, 'reviews/review-list.html', {
        'store': store,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'avg_star_count': avg_star_count,
        'stars_list': stars_list,
        'rating_counts': rating_counts,
        'sort': sort,
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
    reviews = Review.objects.filter(user=request.user).prefetch_related('images', 'likes').order_by('-created_at')
    now = timezone.now()
    # 별점 표시용
    for review in reviews:
        review.stars = "★" * review.rating

        # 날짜 차이 계산
        delta = now - review.created_at
        days = delta.days
        review.natural_days = f"{days}일 전" if days > 0 else "오늘"


    return render(request, 'reviews/my-review.html', {
        'reviews': reviews,
    })
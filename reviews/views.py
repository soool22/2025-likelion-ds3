from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from datetime import timedelta
from django.utils import timezone
from .models import *
from stores.models import Store
from collections import Counter

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
    reviews = Review.objects.filter(store=store).prefetch_related('images').order_by('-created_at')

    # 평균 평점 (모델에 저장되어 있음)
    avg_rating = store.rating
    avg_star_count = int(round(avg_rating))  # 반올림해서 별 개수

    # 별 리스트 1~5
    stars_list = range(1, 6)

    # 별점별 리뷰 개수 (1~5)
    rating_counts = {}
    for i in range(1, 6):
        rating_counts[i] = reviews.filter(rating=i).count()

    return render(request, 'reviews/review-list.html', {
        'store': store,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'avg_star_count': avg_star_count,
        'stars_list': stars_list,
        'rating_counts': rating_counts,
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
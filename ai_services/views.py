from django.shortcuts import get_object_or_404, render
from stores.models import Store
from .services import summarize_reviews
from users.models import UserPreference
import openai

def review_summary(request, store_id):
    """
    가게 상세 페이지에서 리뷰 전체 요약 + 원문 일부 제공
    """
    store = get_object_or_404(Store, id=store_id)

    # 모든 리뷰 텍스트 합치기
    reviews_text = " ".join([r.comment for r in store.reviews.all()])
    print("views.py에서 리뷰 텍스트:", reviews_text)  # 로그 확인용

    # AI 요약 & 원문 일부
    result = summarize_reviews(reviews_text) if reviews_text else {"summary": [], "keywords": [], "snippet": ""}
    print("views.py에서 요약 결과:", result)  # 요약 결과 로그 확인용
    
    

    context = {
        'store': store,
        'ai_summary': result['summary'],       # 요약 문장 리스트
        'review_keywords': result['keywords'], # 키워드 리스트
        'snippet': result['snippet'],          # 원문 일부
    }

    # store_detail 페이지에서 바로 보여주도록 렌더링
    return render(request, 'stores/store_detail.html', context)




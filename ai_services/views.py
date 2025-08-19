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



def store_recommend(request):
    # 사용자 선호 가져오기
    print("MAIN VIEW 호출됨")
    preference = UserPreference.objects.get(user=request.user)
    
    categories = preference.preferred_categories.split(",") if preference.preferred_categories else []
    tastes = preference.preferred_tastes.split(",") if preference.preferred_tastes else []
    price_ranges = preference.preferred_price_ranges.split(",") if preference.preferred_price_ranges else []
    health_options = preference.preferred_health.split(",") if preference.preferred_health else []

    # 가게 데이터 가져오기
    stores = list(Store.objects.values("name", "category", "menu", "description"))

    # LLM 프롬프트 생성
    prompt = f"""
    사용자 선호:
    - 카테고리: {', '.join(categories)}
    - 맛: {', '.join(tastes)}
    - 가격대: {', '.join(price_ranges)}
    - 건강: {', '.join(health_options)}

    아래 가게 정보 중 사용자의 선호에 맞는 가게 5개를 JSON 형태로 추천해줘.
    각 항목에는 "name"과 "reason"만 포함하고, 리스트 형식으로 반환:

    """
    for store in stores:
        prompt += f"{store['name']} - {store['category']}, 메뉴: {', '.join(store['products'])}, 설명: {store['description']}\n"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    # LLM 결과 JSON 파싱
    import json
    try:
        recommended_stores = json.loads(response.choices[0].message.content)
        print(recommended_stores)
    except:
        # 혹시 JSON 파싱 실패 시 그냥 텍스트로 출력
        recommended_stores = [{"name": "추천 실패", "reason": response.choices[0].message.content}]

    return render(request, "home/main.html", {"recommended_stores": recommended_stores})
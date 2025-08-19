import os
import openai
from openai import OpenAI
from dotenv import load_dotenv
from stores.models import Store
from django.utils import timezone
from users.models import UserPreference
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import json
from stores.models import Store
from datetime import timedelta


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

#리뷰 요약

def summarize_reviews(store: Store, snippet_length=50):
    reviews = store.reviews.all()
    reviews_text = " ".join([r.comment for r in reviews])
    
    if not reviews_text:
        store.review_summary_text = ""
        store.review_keywords = ""
        store.review_snippet = ""
        store.review_summary_updated = timezone.now()
        store.save()
        return store

    prompt = (
        "리뷰 내용을 읽고, 한국어로 핵심 키워드 3~5개와 한 문장 요약을 아래 형식으로 출력하세요.\n"
        "키워드는 명사나 간단한 형용사 형태로 나열하고, 각 키워드는 한글로 작성해주세요.\n"
        "그 키워드를 바탕으로 가게에 대해 20자 이내 한 문장으로 요약하되, 분위기/맛/서비스/청결 등을 위주로 작성하세요."
        "개인의 경험이나 불필요한(무의미한) 내용을 배제하고 반드시 '~해요. ~한 평이 많아요.' 투의 친절한 존댓말을 사용하며 부정적 경험은 간접적인 표현을 사용하세요.\n"
        "형식:\n"
        "키워드: 키워드1, 키워드2, ...\n"
        "요약: 한 문장 요약\n\n"
        f"리뷰 내용:\n{reviews_text}"
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 한국어 리뷰 요약 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=150
        )

        result_text = response.choices[0].message.content.strip()
        
        # 키워드와 요약 확실히 분리
        keywords, summary_sentence = "", ""
        for line in result_text.splitlines():
            line = line.strip()
            if line.startswith("키워드:"):
                keywords = line.replace("키워드:", "").strip()
            elif line.startswith("요약:"):
                summary_sentence = line.replace("요약:", "").strip().strip('"')  # 쌍따옴표 제거

        snippet = reviews_text[:snippet_length] + ("..." if len(reviews_text) > snippet_length else "")
        
        store.review_summary_text = summary_sentence
        store.review_keywords = keywords
        store.review_snippet = snippet
        store.review_summary_updated = timezone.now()
        store.save()

    except Exception as e:
        print("OpenAI 요약 오류:", e)
        snippet = reviews_text[:snippet_length] + ("..." if len(reviews_text) > snippet_length else "")
        store.review_summary_text = ""
        store.review_keywords = ""
        store.review_snippet = snippet
        store.review_summary_updated = timezone.now()
        store.save()

    return store

#------------------------------------------------------------------------------------

#관심 기반 가게 추천

# OpenAI 클라이언트 생성
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def store_recommend(user):
    preference = UserPreference.objects.get(user=user)

    # 마지막 추천 갱신 30분 이상 지났는지 확인
    if preference.last_ai_call_time and timezone.now() - preference.last_ai_call_time < timedelta(minutes=30):
        # 30분 미만이면 이전 추천 결과 반환
        return preference.last_ai_recommendation

    # --- 새 AI 호출 로직 ---
    categories = preference.preferred_categories.split(",") if preference.preferred_categories else []
    tastes = preference.preferred_tastes.split(",") if preference.preferred_tastes else []
    price_ranges = preference.preferred_price_ranges.split(",") if preference.preferred_price_ranges else []
    health_options = preference.preferred_health.split(",") if preference.preferred_health else []

    stores = list(Store.objects.values("name", "category", "products", "description"))

    # 프롬프트 생성
    prompt =f"""
    사용자 선호:
    - 카테고리: {', '.join(categories)}
    - 맛: {', '.join(tastes)}
    - 가격대: {', '.join(price_ranges)}
    - 건강: {', '.join(health_options)}

    아래 가게 정보 중 사용자의 선호에 맞는 가게 5개를 JSON 리스트로 추천해 주세요.
    반드시 정확한 JSON 형식으로 반환하고, 리스트 안 객체에는 "name"과 "reason"만 포함하세요.
    매장의 분위기와 메뉴 위주로 설명하세요.
    직접적인 가격대(중가, 고가)를 언급하지 마세요.
    만약 추천할 가게가 없으면 빈 리스트 []를 반환하세요.

    가게 정보 예시:
    [
    {{"name": "가게이름", "reason": "추천 이유"}}
    ]

    """

    for store in stores:
        menu = store.get("products") or ""
        desc = store.get("description") or ""
        prompt += f"{store['name']} - {store['category']}, 메뉴: {menu}, 설명: {desc}\n"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        response_text = response.choices[0].message.content.strip()
        try:
            recommended_stores = json.loads(response_text)
        except json.JSONDecodeError:
            recommended_stores = [{"name": "추천 실패", "reason": response_text or "AI 응답이 비어있음"}]

    except Exception as e:
        recommended_stores = [{"name": "추천 실패", "reason": str(e)}]

    # 캐시에 저장
    preference.last_ai_recommendation = recommended_stores
    preference.last_ai_call_time = timezone.now()
    preference.save()

    return recommended_stores

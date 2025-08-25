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
    preference, _ = UserPreference.objects.get_or_create(user=user)

    # 캐시가 없거나 30분 이상 지난 경우 새 호출
    if not preference.last_ai_recommendation or \
       not preference.last_ai_call_time or \
       timezone.now() - preference.last_ai_call_time >= timedelta(minutes=5):

        categories = preference.preferred_categories.split(",") if preference.preferred_categories else []
        tastes = preference.preferred_tastes.split(",") if preference.preferred_tastes else []
        price_ranges = preference.preferred_price_ranges.split(",") if preference.preferred_price_ranges else []
        health_options = preference.preferred_health.split(",") if preference.preferred_health else []

        stores = list(Store.objects.values("id", "name", "category", "products", "description"))

        prompt = f"""
        사용자 선호:
        - 카테고리: {', '.join(categories) or '없음'}
        - 맛: {', '.join(tastes) or '없음'}
        - 가격대: {', '.join(price_ranges) or '없음'}
        - 건강: {', '.join(health_options) or '없음'}

        아래 가게 정보 중 사용자의 선호와 최대한 맞는 가게 5개를 JSON 리스트로 추천해 주세요.
        리스트 안 객체에는 "id"와 "name"만 포함하세요.
        선호 카테고리가 있을 경우 반드시 해당 카테고리의 가게를 우선 추천하세요.
        가게 정보 예시:
        [{{"id": n, "name": "가게이름"}}]
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
            print("AI response:", response_text)

            try:
                recommended_stores = json.loads(response_text)
            except json.JSONDecodeError:
                recommended_stores = []

            # DB에서 id 붙이기
            final_stores = []
            for s in recommended_stores:
                try:
                    store_obj = Store.objects.get(name=s["name"])
                    final_stores.append({"id": store_obj.id, "name": store_obj.name})
                except Store.DoesNotExist:
                    continue

            # 캐시에 저장
            preference.last_ai_recommendation = final_stores
            preference.last_ai_call_time = timezone.now()
            preference.save()

            return final_stores

        except Exception as e:
            # AI 호출 실패 시 빈 리스트 반환
            preference.last_ai_recommendation = []
            preference.last_ai_call_time = timezone.now()
            preference.save()
            return []
    
    # 캐시 사용
    return preference.last_ai_recommendation

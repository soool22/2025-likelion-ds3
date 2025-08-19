import os
import openai
from dotenv import load_dotenv
from stores.models import Store
from django.utils import timezone

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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

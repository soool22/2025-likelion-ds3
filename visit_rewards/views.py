from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponse
from .models import Store, Visit
import uuid
import base64
import qrcode
from io import BytesIO
from django.contrib.auth.decorators import login_required

# 방문 인증 페이지 + QR 생성
def visit_check(request):
    # 테스트용 가게 가져오기
    store = Store.objects.first()
    if not store:
        return HttpResponse("테스트용 가게가 없습니다.")

    # QR 토큰 생성
    if not store.qr_token:
        store.qr_token = uuid.uuid4().hex
        store.save()

    # 방문 인증 API URL 생성
    qr_url = f"{request.scheme}://{request.get_host()}/visit_rewards/visit/?token={store.qr_token}&test=1"
    print("QR URL:", qr_url)  # 로그 확인

    # QR 코드 생성
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    qr_base64 = base64.b64encode(buf.read()).decode('utf-8')
    store_qr_url = f"data:image/png;base64,{qr_base64}"

    return render(request, 'visit_rewards/visit_checking.html', {
        'store': store,
        'store_qr_url': store_qr_url,
        'qr_url': qr_url,  # JS fetch용
    })


@login_required  # 로그인한 사용자만 방문 인증 가능
def visit_store(request):
    token = request.GET.get("token")
    if not token:
        return JsonResponse({"status": "error", "message": "token이 없습니다."}, status=400)

    try:
        is_test = bool(int(request.GET.get("test", 0)))
    except ValueError:
        is_test = False

    store = get_object_or_404(Store, qr_token=token)

    if not is_test and Visit.objects.filter(store=store, user=request.user).exists():
        return JsonResponse({"status": "already_visited"})

    # user 필드 필수라서 반드시 request.user 포함
    Visit.objects.create(store=store, test=is_test, user=request.user)

    total_visits = Visit.objects.filter(store=store).count()

    return JsonResponse({
        "status": "ok",
        "store_name": store.name,
        "total_visits": total_visits
    })
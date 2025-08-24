import qrcode
from io import BytesIO
from django.core.files import File

def generate_store_qr(store, host="localhost:8000", test=False):
    """
    QR 코드 생성 (File 객체 + QR URL)
    """
    qr_url = f"http://{host}/visit?token={store.qr_token}&test={int(test)}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    qr_file = File(buffer, name=f"{store.name}_qr.png")
    return qr_file, qr_url  # ✅ 2개 반환


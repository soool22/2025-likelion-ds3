import qrcode
from io import BytesIO
from django.core.files import File

def generate_store_qr(store, test=False):
    """
    QR 코드 생성 (테스트용 포함)
    """
    qr_url = f"http://localhost:8000/visit?token={store.qr_token}&test={int(test)}"

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

    return File(buffer, name=f"{store.name}_qr.png")

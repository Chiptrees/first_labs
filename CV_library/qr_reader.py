import qrcode
import json
import numpy as np

def create_qr(data: dict):

    json_string = json.dumps(data, ensure_ascii=False)

    # Створюємо QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,
        border=4,
    )
    qr.add_data(json_string)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return np.array(img.convert("RGB"))


import qrcode
from db import find_photo_names
def generate_qr(user_id, user_name, first_name, last_name, x):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=25,
        border=4
    )

    qr.add_data(f"user_id : {user_id}, user_name : {user_name}, first_name: {first_name}, last_name{last_name}, тип : {x}")
    img = qr.make_image()
    put = 'qr_codes/'f'{user_id}_{x}.jpg'
    img.save(f'{put}', 'JPEG')

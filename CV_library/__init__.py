from .bilinear_invertor import *
from .qr_reader import *
import numpy as np
import cv2
import os

def get_variant(lab_number, key_word: str, len_numbers=None, min_value=-100, max_value=100):
    if lab_number == 1:
        rng = np.random.default_rng(__text_seed(key_word))
        area1 = np.array([[[100, 250], [250, 200]],
                          [[50, 100], [200, 50]]])
        while True:
            area2 = np.array([[[100, 200], [200, 200]],
                              [[100, 100], [200, 100]]]) + rng.integers(-45, 46, (2, 2, 2))
            try:
                Area(*area2.reshape((-1, 2)))
                break
            except Exception:
                pass

        grid1 = np.array([[[50, 250], [150, 250], [250, 250]],
                          [[50, 150], [150, 150], [250, 150]],
                          [[50,  50], [150,  50], [250,  50]]])
        while True:
            grid2 = grid1 + rng.integers(-45, 46, (3, 3, 2))
            try:
                for i, j in [(0, 0), (0, 1), (1, 0), (1, 1)]:
                    Area(*grid2[i:i+2, j:j+2, :].reshape((-1, 2)))
                break
            except Exception as e:
                pass




        points = np.array([[170,  190], [120, 200], [150, 120]])
        line_poly = np.poly1d([0.5, 50])
        cubic_poly = np.poly1d([0.00007, -0.033, 4, 80])


        return {
            'area1': area1,
            'area2': area2,

            'grid1': grid1,
            'grid2': grid2,

            'points':   points,
            'line':     line_poly,
            'polynom':  cubic_poly
        }

    elif lab_number == 2:
        pass

    elif lab_number == 3:
        seed = __text_seed(key_word)
        rng = np.random.default_rng(seed)
        qr_data1 = {name: part for name, part in zip(['Last Name', 'First Name', 'Middle Name', 'other'],
                                                    key_word.split(' ', 3))}
        qr_data2 = {'your_seed': seed}
        qr_data3 = {'short_review': [lab_number, key_word, seed]}
        qr_data4 = {'QR': 'Nothing interesting, just another dict'}

        for path in [
            'dataset/images/train/',
            'first_labs/dataset/images/train/'
        ]:
            if os.path.exists(path):
                break
        else:
            raise FileNotFoundError(
                'Cannot find dataset'
            )

        photos = [np.flip(cv2.imread(path + name), axis=2) for name in rng.choice(names, 3)]

        images = []
        qr_data = [qr_data1, qr_data2, qr_data3, qr_data4]

        for photo, qr_count in zip(photos, [1, 2, 4]):

            img = photo.copy()
            placed = []
            for i in range(qr_count):
                qr = qr_data[i]
                qr = __rotate_image(create_qr(qr), rng.uniform(-40, 40))
                rect = __find_position(rng, qr.shape, placed)
                __overlay_rgba(img, qr, rect[0], rect[1])
                placed.append(rect)

            images.append(img)

        return {f'image{i}': image for i, image in enumerate(images)}
    else:
        if len_numbers is None:
            raise Exception('You use custom mode, so you need to provide len numbers')

        return __word_convertor(key_word, len_numbers, min_value, max_value)


def __text_seed(word) -> int:
    seed = 0
    for i, ch in enumerate(word):
        seed += (i + 1) * ord(ch) ** 2
    return seed % (2 ** 32)


def __word_convertor(fio, len_numbers, min_value, max_value):
    rng = np.random.default_rng(__text_seed(fio))

    return rng.integers(
        min_value,
        max_value + 1,
        size=len_numbers,
        dtype=np.int32
    )

def __rotate_image(img, angle, border=0):
    # якщо зображення RGB -> додаємо альфа-канал
    if img.shape[2] == 3:
        alpha = np.full(
            img.shape[:2],
            255,
            dtype=np.uint8
        )

        img = np.dstack([img, alpha])

    # біла рамка навколо QR
    img = cv2.copyMakeBorder(
        img,
        border,
        border,
        border,
        border,
        cv2.BORDER_CONSTANT,
        value=(255, 255, 255, 255)
    )

    h, w = img.shape[:2]

    M = cv2.getRotationMatrix2D(
        (w / 2, h / 2),
        angle,
        1.0
    )

    cos = abs(M[0, 0])
    sin = abs(M[0, 1])

    nw = int(h * sin + w * cos)
    nh = int(h * cos + w * sin)

    M[0, 2] += nw / 2 - w / 2
    M[1, 2] += nh / 2 - h / 2

    return cv2.warpAffine(
        img,
        M,
        (nw, nh),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0)   # прозорий фон
    )

def __intersect(rect1, rect2):

    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    return not (
        x1 + w1 <= x2 or
        x2 + w2 <= x1 or
        y1 + h1 <= y2 or
        y2 + h2 <= y1
    )

def __find_position(
        rng,
        qr_shape,
        placed,
        W=640,
        H=480):

    h, w = qr_shape[:2]

    for _ in range(1000):

        x = rng.integers(
            0,
            W - int(w)
        )

        y = rng.integers(
            0,
            H - int(h)
        )

        rect = (x, y, w, h)

        good = True

        for old in placed:
            if __intersect(rect, old):
                good = False
                break

        if good:
            return rect

    raise RuntimeError(
        "Cannot place QR code"
    )

"""def __place_qr(background,
             qr,
             rect):

    x, y, w, h = rect

    roi = background[
        y:y+h,
        x:x+w
    ]

    mask = cv2.cvtColor(
        qr,
        cv2.COLOR_BGR2GRAY
    )

    _, mask = cv2.threshold(
        mask,
        250,
        255,
        cv2.THRESH_BINARY_INV
    )

    roi[mask > 0] = qr[mask > 0]

    return background"""

def __overlay_rgba(background, qr, x, y):

    h, w = qr.shape[:2]

    roi = background[y:y+h, x:x+w]

    alpha = qr[..., 3:4] / 255.0

    roi[:] = (
        roi * (1 - alpha)
        + qr[..., :3] * alpha
    ).astype(np.uint8)

    return background

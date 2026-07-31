from .bilinear_invertor import *
import numpy as np

def get_variant(lab_number, key_word, len_numbers=None, min_value=-100, max_value=100):
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
        pass

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

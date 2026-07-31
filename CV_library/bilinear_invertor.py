import numpy as np

class Area:
    eps = 1e-12

    def __init__(self, p00, p01, p10, p11):
        self.p00 = np.array(p00)
        self.p01 = np.array(p01)
        self.p10 = np.array(p10)
        self.p11 = np.array(p11)

        # Перевірка у виордженість у пряму
        self._area = abs(self._cross(self.p01 - self.p00, self.p10 - self.p00))
        if self._area < self.eps:
            raise Exception('quadrilateral close to a straight line')

        self._A = np.array(p01) - np.array(p00)
        self._B = np.array(p10) - np.array(p00)
        self._C = np.array(p00) - np.array(p10) - np.array(p01) + np.array(p11)

        # перевірка на самоперетин
        self._ab = self._cross(self._A, self._B)
        self._ac = self._cross(self._A, self._C)
        self._bc = self._cross(self._B, self._C)
        self._jac_corners = np.array([
            self._ab,
            self._ab + self._ac,
            self._ab + self._bc,
            self._ab + self._ac + self._bc
        ])
        # print(self._jac_corners)
        if not (np.all(self._jac_corners > 0) or np.all(self._jac_corners < 0)):
           raise Exception('The quadrilateral does not define a unique bilinear mapping. Check the vertex order.')

        self._a = -self._cross(self._A, self._C)

    @property
    def affine(self):
        return abs(self._a) < self.eps

    @staticmethod
    def _cross(a, b):
        return a[..., 0] * b[..., 1] - a[..., 1] * b[..., 0]

    def find_xy(self, uv_batch: np.ndarray):
        return self.p00 + self._A * uv_batch[...,0:1] + self._B * uv_batch[...,1:2] + self._C * uv_batch[...,0:1] * uv_batch[...,1:2]


    def find_uv(self, xy_batch: np.ndarray, only_inside=False):
        xy_batch = np.asarray(xy_batch)
        E = xy_batch - self.p00

        a = self._a
        b = self._cross(E, self._C) - self._ab
        c = self._cross(E, self._B)

        if self.affine:
            u = -c / b
        else:
            D = np.maximum(b * b - 4 * a * c, 0.0)

            u1 = (-b + np.sqrt(D)) / (2 * a)
            u2 = (-b - np.sqrt(D)) / (2 * a)

            tol = 1e-12

            in1 = (u1 >= -tol) & (u1 <= 1 + tol)
            in2 = (u2 >= -tol) & (u2 <= 1 + tol)

            u = np.where(
                in1 & ~in2,
                u1,
                np.where(
                    in2 & ~in1,
                    u2,
                    np.where(
                        np.abs(u1) <= np.abs(u2),
                        u1,
                        u2,
                    ),
                ),
            )

        den = self._B + u[..., None] * self._C

        use_x = np.abs(den[..., 0]) > np.abs(den[..., 1])

        v_x = (E[..., 0] - u * self._A[0]) / den[..., 0]
        v_y = (E[..., 1] - u * self._A[1]) / den[..., 1]

        v = np.where(use_x, v_x, v_y)

        ans = np.stack([u, v], axis=-1)
        if only_inside:
            return ans[(u >= -self.eps) &
                (u <= 1 + self.eps) &
                (v >= -self.eps) &
                (v <= 1 + self.eps)]
        return ans

    def contains(self, xy_batch: np.ndarray):
        uv = self.find_uv(xy_batch)

        u = uv[..., 0]
        v = uv[..., 1]

        return (
                (u >= -self.eps) &
                (u <= 1 + self.eps) &
                (v >= -self.eps) &
                (v <= 1 + self.eps)
        )

    @property
    def area(self):
        return np.stack([self.p00, self.p01, self.p11, self.p10], axis=0)
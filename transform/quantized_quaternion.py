from math import fabs

class QuantizedQuaternion:
    SQRT_2 = 1.41421356237
    ONE_OVER_SQRT_2 = 0.70710678118

    @staticmethod
    def compress(quat: list[int, int, int, int]) -> list[int]:
        max_index = 3

        x, y, z, w = quat
        x_abs = fabs(x)
        y_abs = fabs(y)
        z_abs = fabs(z)
        w_abs = fabs(w)

        if x_abs >= w_abs and x_abs >= y_abs and x_abs >= z_abs:
            max_index = 0
            if quat[0] < 0:
                quat = [-x for x in quat]
        elif y_abs >= w_abs and y_abs >= x_abs and y_abs >= z_abs:
            max_index = 1
            if quat[1] < 0:
                quat = [-x for x in quat]
        elif z_abs >= w_abs and z_abs >= x_abs and z_abs >= y_abs:
            max_index = 2
            if quat[2] < 0:
                quat = [-x for x in quat]
        elif quat[3] < 0:
            quat = [-x for x in quat]

        bits = (max_index << 45) & 0xFFFFFFFFFFFFFFFF

        compressed_index = 0
        for i in range(4):
            if i == max_index:
                continue

            component = round(32767.0 / 2.0 * (QuantizedQuaternion.SQRT_2 * quat[i] + 1.0))
            bits |= (component & 0b0111111111111111) << (15 * (2 - compressed_index))

            compressed_index += 1

        return [(bits >> (8 * i)) & 0b11111111 for i in range(6)]

                
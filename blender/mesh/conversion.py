import numpy as np

class DataConversions:
    @staticmethod
    def to_blender_uv(array: np.ndarray):
        array[:, 1] *= -1
        array[:, 1] += 1
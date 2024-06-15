from mathutils import Vector, Quaternion
from math import isclose
import numpy as np

class TransformStorage:
    TransformTolerance = 0.0375
    RotationTolerance = 0.00385
    
    def __init__(self) -> None:
        self.transforms: list[Vector] = []
        self.rotations: list[Quaternion] = []
        
        self.translation_indices: list[int] = []
        self.scale_indices: list[int] = []
        self.rotation_indices: list[int] = []
        
        self.indices: np.ndarray = np.array([], dtype=np.uint16)
        
    def indices_from_buffer(self, data: bytes, offset: int, frames_count: int, joints_count: int) -> None:
        array = np.frombuffer(data, offset=offset, dtype=np.uint16, count=(frames_count * joints_count) * 3)
        self.indices = np.reshape(array, (frames_count * joints_count, 3))
        
    def indices_from_count(self, frames_count: int, joints_count: int) -> None:
        self.indices = np.zeros((frames_count * joints_count, 3), dtype=np.uint16)
        
    def add_translation(self, value: Vector, offset: int):
        index = len(self.transforms)
        self.set_translation_index(index, offset)
        self.transforms.append(value)
        return index
    
    def set_translation_index(self, index: int, offset: int):
        self.indices[offset][0] = index
    
    def add_scale(self, value: Vector, offset: int):
        index = len(self.transforms)
        self.set_scale_index(index, offset)
        self.transforms.append(value)
        return index
    
    def set_scale_index(self, index: int, offset: int):
        self.indices[offset][1] = index
    
    def add_rotation(self, value: Quaternion, offset: int):
        index = len(self.rotations)
        self.set_rotation_index(index, offset)
        self.rotations.append(value)
        return index
    
    def set_rotation_index(self, index: int, offset: int):
        self.indices[offset][2] = index
    
    def set_translation_approx(self, value: Vector, offset: int) -> int:
        for i, other in enumerate(self.transforms):
            if isclose(value.x, other.x, rel_tol=TransformStorage.TransformTolerance) and \
                isclose(value.y, other.y, rel_tol=TransformStorage.TransformTolerance) and \
                isclose(value.z, other.z, rel_tol=TransformStorage.TransformTolerance):
                    self.set_translation_index(i, offset)
                    return i
        
        return self.add_translation(value, offset)
    
    def set_translation_rough(self, value: Vector, offset: int) -> int:
        for i, other in enumerate(self.transforms):
            if other == value:
                    self.set_translation_index(i, offset)
                    return i
        
        return self.add_translation(value, offset)
    
    def set_scale_approx(self, value: Vector, offset: int) -> int:
        for i, other in enumerate(self.transforms):
            if isclose(value.x, other.x, rel_tol=TransformStorage.TransformTolerance) and \
                isclose(value.y, other.y, rel_tol=TransformStorage.TransformTolerance) and \
                isclose(value.z, other.z, rel_tol=TransformStorage.TransformTolerance):
                    self.set_scale_index(i, offset)
                    return i
        
        return self.add_scale(value, offset)
    
    def set_scale_rough(self, value: Vector, offset: int) -> int:
        for i, other in enumerate(self.transforms):
            if other == value:
                    self.set_scale_index(i, offset)
                    return i
        
        return self.add_scale(value, offset)
        
    def set_rotation_approx(self, value: Vector, offset: int) -> int:
        for i, other in enumerate(self.rotations):
            if isclose(value.x, other.x, rel_tol=TransformStorage.RotationTolerance) and \
                isclose(value.y, other.y, rel_tol=TransformStorage.RotationTolerance) and \
                isclose(value.z, other.z, rel_tol=TransformStorage.RotationTolerance) and \
                isclose(value.w, other.w, rel_tol=TransformStorage.RotationTolerance):
                    self.set_rotation_index(i, offset)
                    return i
        
        return self.add_rotation(value, offset)

    def set_rotation_rough(self, value: Vector, offset: int):
        for i, other in enumerate(self.rotations):
            if other == value:
                    self.set_rotation_index(i, offset)
                    return
        
        return self.add_rotation(value, offset)
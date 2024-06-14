from mathutils import Vector, Quaternion
from math import isclose

class TransformStorage:
    TransformTolerance = 0.0375
    RotationTolerance = 0.00385
    
    def __init__(self) -> None:
        self.transforms: list[Vector] = []
        self.rotations: list[Quaternion] = []
        
        self.translation_indices: list[int] = []
        self.scale_indices: list[int] = []
        self.rotation_indices: list[int] = []
    
    def add_translation(self, value: Vector) -> None:
        for i, other in enumerate(self.transforms):
            if isclose(value.x, other.x, rel_tol=TransformStorage.TransformTolerance) and \
                isclose(value.y, other.y, rel_tol=TransformStorage.TransformTolerance) and \
                isclose(value.z, other.z, rel_tol=TransformStorage.TransformTolerance):
                    self.translation_indices.append(i)
                    return i
        
        index = len(self.transforms)
        self.translation_indices.append(index)
        self.transforms.append(value)
        return index
    
    def add_scale(self, value: Vector) -> None:
        for i, other in enumerate(self.transforms):
            if isclose(value.x, other.x, rel_tol=TransformStorage.TransformTolerance) and \
                isclose(value.y, other.y, rel_tol=TransformStorage.TransformTolerance) and \
                isclose(value.z, other.z, rel_tol=TransformStorage.TransformTolerance):
                    self.scale_indices.append(i)
                    return i
        
        index = len(self.transforms)
        self.scale_indices.append(index)
        self.transforms.append(value)
        return index
        
    def add_rotation(self, value: Vector) -> int:
        for i, other in enumerate(self.rotations):
            if isclose(value.x, other.x, rel_tol=TransformStorage.RotationTolerance) and \
                isclose(value.y, other.y, rel_tol=TransformStorage.RotationTolerance) and \
                isclose(value.z, other.z, rel_tol=TransformStorage.RotationTolerance) and \
                isclose(value.w, other.w, rel_tol=TransformStorage.RotationTolerance):
                    self.rotation_indices.append(i)
                    return i
        
        index = len(self.rotations)
        self.rotation_indices.append(index)
        self.rotations.append(value)
        return index
        
    def add_translation_rough(self, value: Vector):
        for i, other in enumerate(self.transforms):
            if other == value:
                    self.translation_indices.append(i)
                    return
        
        self.translation_indices.append(len(self.transforms))
        self.transforms.append(value)
        
    def add_scale_rough(self, value: Vector):
        for i, other in enumerate(self.transforms):
            if other == value:
                    self.scale_indices.append(i)
                    return
        
        self.scale_indices.append(len(self.transforms))
        self.transforms.append(value)
        
    def add_rotation_rough(self, value: Vector):
        for i, other in enumerate(self.rotations):
            if other == value:
                    self.rotation_indices.append(i)
                    return
        
        self.rotation_indices.append(len(self.rotations))
        self.rotations.append(value)
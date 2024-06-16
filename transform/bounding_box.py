from mathutils import Vector

class BoundingBox:
    def __init__(self) -> None:
        self.min = Vector()
        self.max = Vector()
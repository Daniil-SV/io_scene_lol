from mathutils import Vector

class BoundingSphere:
    def __init__(self) -> None:
        self.center: Vector = Vector()
        self.radius: float = 0.0
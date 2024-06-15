from mathutils import Vector, Quaternion, Matrix
from ...reader import Stream

class SkeletonJoint:
    def __init__(self) -> None:
        self.name = ""
        self.id: int = 0
        self.parent: int = 0
        self.radius: float = 2.1
        
        self.translation = Vector()
        self.scale = Vector((1, 1, 1))
        self.rotation = Quaternion()
        
        self.inverse_translation = Vector()
        self.inverse_scale = Vector((1, 1, 1))
        self.inverse_rotation = Quaternion()
        
    def read(self, stream: Stream):
        # Flags
        stream.read_uint16()
        
        self.id = stream.read_uint16()
        self.parent = stream.read_uint16()
        
        # Unknown
        stream.read_uint16()
        
        self.hash = stream.read_bytes(4)
        self.radius = stream.read_float()
        
        self.translation = stream.read_vector()
        self.scale = stream.read_vector()
        self.rotation = stream.read_quaternion()
        
        self.inverse_translation = stream.read_vector()
        self.inverse_scale = stream.read_vector()
        self.inverse_rotation = stream.read_quaternion()
        
        name_local_offset = stream.pos()
        name_offset = stream.read_uint32()
        
        pos = stream.pos()
        stream.seek(name_offset + name_local_offset)
        self.name = stream.read_str()
        stream.seek(pos)
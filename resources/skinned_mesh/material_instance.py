from bpy.types import Material
from ...reader import Stream
from ...blender.mesh.material_instance import MeshMaterialInstance

class SkinnedMeshMaterialInstance(MeshMaterialInstance):
    def __init__(self) -> None:
        super().__init__()
        
    def read(self, stream: Stream) -> None:
        self.name = stream.read_str()
        
        if (len(self.name) >= 64):
            raise ValueError("Material name string is too long!")
        
        pad_length = 64 - (len(self.name) + 1)
        stream.read_bytes(pad_length)
        
        self.vertex_offset = stream.read_uint32()
        self.vertex_count = stream.read_uint32()
        self.indices_offset = stream.read_uint32()
        self.indices_count = stream.read_uint32()
    
    # A little bit of blender in resources module...
    def produce_material(self) -> Material:
        return super().produce_material()
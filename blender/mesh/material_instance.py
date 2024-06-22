import bpy
from ...reader import Stream
from abc import abstractmethod

class MeshMaterialInstance:
    def __init__(self) -> None:
        self.name: str = ""
        self.vertex_count = 0
        self.vertex_offset = 0
        self.indices_count = 0
        self.indices_offset = 0
    
    @abstractmethod
    def read(self, stream: Stream) -> None:
        pass
    
    @abstractmethod
    def produce_material(self) -> bpy.types.Material:
        material = bpy.data.materials.new(self.name)
        material.use_nodes = True
        
        return material
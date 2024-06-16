import numpy as np
from .material_instance import SkinnedMeshMaterialInstance
from enum import IntEnum
from ...reader import Stream
from ...reader.binary_reader import Whence
from ...transform.bounding_box import BoundingBox
from ...transform.bounding_sphere import BoundingSphere

class SkinnedMeshAsset:
    class VertexType(IntEnum):
        Default = 0 # POSITION, JOINT, WEIGHT, NORMAL, TEXCOORD vector
        Colored = 1 # COLOR vector
        Curved = 2 # TANGENT vector
    
    def __init__(self) -> None:
        self.materials: list[SkinnedMeshMaterialInstance] = []
        self.indices: np.ndarray = np.array([], dtype=np.uint16)
        self.vertex_type = SkinnedMeshAsset.VertexType.Default
        self.vertices: np.ndarray = np.array([], dtype=np.float32)
        
        self.bounding_box = BoundingBox()
        self.bounding_sphere = BoundingSphere()
        
    def read(self, filepath: str) -> None:
        with open(filepath, "rb") as file:
            data = file.read()
        
        self.read_stream(Stream(data))
    
    def read_stream(self, stream: Stream) -> None:
        magic = stream.read_uint32()
        
        if (magic != 0x00112233):
            raise ValueError(f"File is corrupted or has wrong magic number: {magic}")
        
        version = stream.read_uint16()
        revision = stream.read_uint16()
        
        match(version):
            case 1 | 2 | 3 | 4:
                self.read_asset(stream, version, revision)
            case _:
                raise ValueError(f"Unknown Skinned Mesh Asset version {version}")
    
    def read_asset(self, stream: Stream, version: int, revision: int) -> None:
        materials_count = stream.read_uint32()
        self.materials = [SkinnedMeshMaterialInstance() for _ in range(materials_count)]
        
        for material in self.materials:
            material.read(stream)
        
        if (version == 4):
            # Flags
            stream.read_uint32()
        
        indices_count = stream.read_uint32()
        vertices_count = stream.read_uint32()
        vertex_stride = 52
        
        if (version == 4):
            vertex_stride = stream.read_uint32()
            self.vertex_type = SkinnedMeshAsset.VertexType(stream.read_uint32())
            
            self.bounding_box.min = stream.read_vector()
            self.bounding_box.max = stream.read_vector()
            
            self.bounding_sphere.center = stream.read_vector()
            self.bounding_sphere.radius = stream.read_float()
            
        
        self.indices = np.frombuffer(
            stream.buffer(),
            np.uint16,
            indices_count,
            stream.pos()
        )
        stream.seek(indices_count * 2, Whence.CUR)
        
        if (vertex_stride % 4 != 0):
            raise ValueError("Vertex stride is not a multiple of 4")
        
        elements_count = vertex_stride // 4
        self.vertices = np.reshape(
            np.frombuffer(
                stream.buffer(),
                np.float32,
                vertices_count * elements_count,
                stream.pos()
            ),
            (vertices_count, elements_count)
        )
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
        self.vertex_data: np.ndarray = np.array([], dtype=np.float32)
        
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
        
        if (indices_count % 3 != 0):
            raise ValueError("Indices count is not a multiple of 3")
        
        self.indices = np.reshape(
            np.frombuffer(
                stream.buffer(),
                np.uint16,
                indices_count,
                stream.pos()
            ),
            (indices_count // 3, 3)
        )
        stream.seek(indices_count * 2, Whence.CUR)
        
        if (vertex_stride % 4 != 0):
            raise ValueError("Vertex stride is not a multiple of 4")
        
        self.vertex_data = np.frombuffer(
                stream.buffer(),
                self.dtype,
                vertices_count,
                stream.pos()
        )
        
    @property
    def has_color(self):
        return int(self.vertex_type) >= SkinnedMeshAsset.VertexType.Colored
    
    @property
    def has_tangent(self):
        return int(self.vertex_type) >= SkinnedMeshAsset.VertexType.Curved
    
    @property
    def dtype(self) -> np.dtype:
        fields = [
            ('x', np.float32), ('y', np.float32), ('z', np.float32),                                                # Position
            ('bone_1', np.ubyte), ('bone_2', np.ubyte), ('bone_3', np.ubyte), ('bone_4', np.ubyte),                 # Bone Weight Index
            ('weight_1', np.float32), ('weight_2', np.float32), ('weight_3', np.float32), ('weight_4', np.float32), # Bone Weight Influence
            ('nx', np.float32), ('ny', np.float32), ('nz', np.float32),                                             # Normal
            ('u', np.float32), ('v', np.float32)                                                                    # Texcoord
        ]
        
        if self.has_color:
            fields += [
                ('r', np.ubyte), ('g', np.ubyte), ('b', np.ubyte), ('a', np.ubyte)
            ]
        
        if self.has_tangent:
            fields += [
                ('tx', np.float32), ('ty', np.float32), ('tz', np.float32), ('tw', np.float32)
            ]
        
        return np.dtype(fields)
    
    @property
    def vertices(self) -> np.ndarray:
        array = np.zeros(
            (len(self.vertex_data), 3), 
            dtype=np.float32
        )
        
        array[:, 0] = self.vertex_data["x"]
        array[:, 1] = self.vertex_data["y"]
        array[:, 2] = self.vertex_data["z"]

        return array
    
    @property
    def texcoord(self) -> np.ndarray:
        array = np.zeros(
            (len(self.vertex_data), 2), 
            dtype=np.float32
        )
        
        array[:, 0] = self.vertex_data["u"]
        array[:, 1] = self.vertex_data["v"]
        
        return array
    
    @property
    def normals(self) -> np.ndarray:
        array = np.zeros(
            (len(self.vertex_data), 3), 
            dtype=np.float32
        )
        
        array[:, 0] = self.vertex_data["nx"]
        array[:, 1] = self.vertex_data["ny"]
        array[:, 2] = self.vertex_data["nz"]
        
        return array
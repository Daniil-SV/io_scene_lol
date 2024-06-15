from .joint import SkeletonJoint
from .joint_instance import SkeletonJointInstance
from ...reader import Stream
from ...reader.binary_reader import Whence
import numpy as np

class SkeletonAsset:
    def __init__(self) -> None:
        self.joints: list[SkeletonJoint] = []
        self.instances: list[SkeletonJointInstance] = []
        self.joints_names: list[str] = []
        
        self.vertex_weight_map: np.ndarray = np.array([], dtype=np.uint16)
        self.name_hash = b"\0\0\0\0"
        self.asset_name_hash = b"\0\0\0\0"
    
    def get_joint_by_id(self, id: int) -> SkeletonJoint | None:
        return next(
            (joint for joint in self.joints if joint.id == id), 
            None,
        )
    
    def get_instance_by_hash(self, hash: bytes) -> SkeletonJointInstance | None:
        return next(
            (instance for instance in self.instances if instance.hash == hash),
            None,
        )
    
    def read(self, filepath: str) -> None:
        with open(filepath, "rb") as file:
            data = file.read()
            
        self.read_stream(Stream(data))
        
    def read_stream(self, stream: Stream) -> None:
        file_size = stream.read_uint32()
        buffer_size = len(stream.buffer())
        
        if (buffer_size != file_size):
            raise ValueError(f"Excepted file size {file_size}, but received buffer with length {buffer_size}")
        
        magic_number = stream.read_uint32()
        if (magic_number != 587026371):
            raise ValueError(f"Corrupted or wrong file magic {magic_number}")
        
        version = stream.read_uint32()
        
        match (version):
            case 0:
                self.read_simple_asset(stream)
            
            case _:
                raise ValueError(f"Unexpected Skeleton Asset version: {version}")
            
    def read_simple_asset(self, stream: Stream) -> None:
        # Flags
        stream.read_uint16()

        joints_count = stream.read_uint16()
        self.joints = [SkeletonJoint() for _ in range(joints_count)]
        self.instances = [SkeletonJointInstance() for _ in range(joints_count)]
        
        vertex_map_length = stream.read_uint32()
        
        joints_offset = stream.read_uint32()
        joints_hashes_offset = stream.read_uint32()
        vertex_map_offset = stream.read_uint32()
        name_offset = stream.read_uint32()
        asset_name_offset = stream.read_uint32()
        
        # joints_names_offset
        stream.read_uint32()
        
        # Reserved
        stream.seek(20, Whence.CUR)

        stream.seek(joints_offset)
        for joint in self.joints:
            joint.read(stream)
            
        stream.seek(joints_hashes_offset)
        for instance in self.instances:
            instance.read(stream)

        self.vertex_weight_map = np.frombuffer(
            stream.buffer(),
            np.uint16, 
            vertex_map_length, 
            vertex_map_offset 
        )
        
        stream.seek(name_offset)
        self.name_hash = stream.read_bytes(4)
        
        stream.seek(asset_name_offset)
        self.asset_name_hash = stream.read_bytes(4)
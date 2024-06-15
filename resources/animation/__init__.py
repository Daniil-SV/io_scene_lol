from ...reader import Stream
from ...logger import Logger
from ...transform.quantized_quaternion import QuantizedQuaternion
from ...hashing.elf import Elf
from .transform_storage import TransformStorage

class AnimationAsset:
    Version = 5
    Magic = 'r3d2'
    UncompressedDataMagic = 'anmd'
    
    def __init__(self) -> None:
        self.duration: int = 0
        self.fps: int = 30
        self.joints: list[str] = []
        self.storage = TransformStorage()

    def write(self, write_compressed: bool = False) -> bytes:
        stream = Stream()
        
        Logger.info(f"Writing Animation Asset with version - {AnimationAsset.Version}")
        
        stream.write_str(AnimationAsset.Magic)
        stream.write_str(AnimationAsset.UncompressedDataMagic) 
        stream.write_uint32(AnimationAsset.Version)
        
        data = self.write_uncompressed()
        stream.write_uint32(len(data) + 4)
        stream.write_bytes(data)
        
        return bytes(stream.buffer())
    
    def write_uncompressed(self) -> bytes:
        stream = Stream()

        # Format Token
        stream.write_uint32(0)

        # Data Version
        stream.write_uint32(0)

        # Flags
        stream.write_uint32(0)
        
        # Joints count
        stream.write_uint32(len(self.joints))

        # Frames count
        stream.write_uint32(self.duration)

        # Frame duration
        stream.write_float(1 / self.fps)
        
        palette_buffer_size = 36
        palette_base_offset = stream.pos() + palette_buffer_size + 4

        palette = Stream()
        #! Vectors
        vectors_position  = palette.pos()
        for vector in self.storage.transforms:
            palette.write_float(vector.x)
            palette.write_float(vector.y)
            palette.write_float(vector.z)

        #! Rotations
        rotations_position = palette.pos()
        for rotation in self.storage.rotations:
            for byte in QuantizedQuaternion.compress([rotation.x, rotation.y, rotation.z, rotation.w]):
                palette.write_uint8(byte)

        #! Joint names
        joints_offset = palette.pos()
        for name in self.joints:
            palette.write_uint32(Elf.lower_hash(name))

        #! Frame indices
        frame_data_offset = palette.pos()
        palette.write_bytes(
            self.storage.indices.tobytes()
        )
        #for _ in range(self.duration):
        #    for t in range(len(self.joints)):
        #        # Translation index
        #        palette.write_uint16(self.transformations.translation_indices[frame_elements_offset + t])
#
        #        # Scale index
        #        palette.write_uint16(self.transformations.scale_indices[frame_elements_offset + t])
        #        
        #        # Rotation index 
        #        palette.write_uint16(self.transformations.rotation_indices[frame_elements_offset + t])
        #        
        #    frame_elements_offset += len(self.joints)

        
        # Name hashes offfset
        stream.write_uint32(joints_offset + palette_base_offset)

        # Asset Name Hash
        stream.write_uint32(0)

        # Asset Time Offset
        stream.write_uint32(0)

        # Vectors
        stream.write_uint32(vectors_position + palette_base_offset)

        # Rotations Vector
        stream.write_uint32(rotations_position + palette_base_offset)

        # Frame Data
        stream.write_uint32(frame_data_offset + palette_base_offset)

        # Reserved
        stream.write_bytes(bytes(12))
        
        stream.write_bytes(bytes(palette.buffer()))
        
        return bytes(stream.buffer())

from .binary_reader import BinaryReader, Endian
from mathutils import Vector, Quaternion

class Stream(BinaryReader):
    def __init__(self, buffer = bytearray(), endianness: Endian = Endian.LITTLE, encoding='utf-8'):
        super().__init__(buffer, endianness, encoding)

    def read_vector(self) -> Vector:
        return Vector(
            (self.read_float(),
            self.read_float(),
            self.read_float())
        )
        
    def read_quaternion(self) -> Quaternion:
        return Quaternion(
            (self.read_float(),
            self.read_float(),
            self.read_float(),
            self.read_float())
        )
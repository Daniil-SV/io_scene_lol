from ...reader import Stream

class SkeletonJointInstance:
    def __init__(self) -> None:
        self.id: int = 0
        self.name_hash: bytes = b"\0\0\0\0"
        
    def read(self, stream: Stream):
        self.id = stream.read_uint16()
        stream.read_uint16()
        self.hash = stream.read_bytes(4)
from ...reader import Stream

class SkinnedMeshMaterialInstance:
    def __init__(self) -> None:
        self.name: str = ""
        self.vertex_count = 0
        self.vertex_offset = 0
        self.indices_count = 0
        self.indices_offset = 0
        
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
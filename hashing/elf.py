
class Elf:
    @staticmethod
    def lower_hash(value: str) -> int:
        return Elf.hash(value.lower())
    
    @staticmethod
    def hash(value: str) -> int:
        hash = 0
        high = 0
        for i in range(len(value)):
            hash = (hash << 4) + ord(value[i])

            high = hash & 0xF0000000
            if (high != 0):
                hash ^= high >> 24
        
            hash &= ~high

        return hash
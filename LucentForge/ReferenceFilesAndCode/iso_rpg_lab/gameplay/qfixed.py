class Q8_8:
    __slots__ = ("raw",)
    SCALE = 256  # 1<<8

    def __init__(self, value=0):
        if isinstance(value, float):
            self.raw = int(round(value * self.SCALE))
        elif isinstance(value, Q8_8):
            self.raw = value.raw
        else:
            self.raw = int(value)

    def to_float(self) -> float:
        return self.raw / self.SCALE

    def __add__(self, other):  return Q8_8(self.raw + Q8_8(other).raw)
    def __sub__(self, other):  return Q8_8(self.raw - Q8_8(other).raw)
    def __mul__(self, other):  return Q8_8((self.raw * Q8_8(other).raw) // self.SCALE)
    def __truediv__(self, other): return Q8_8((self.raw * self.SCALE) // Q8_8(other).raw)

    def __repr__(self): return f"Q8_8({self.to_float():.4f})"

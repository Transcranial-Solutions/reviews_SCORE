from iconservice import (
    InterfaceScore,
    Address,
    interface
)

class TokenFallbackInterface(InterfaceScore):
    @interface
    def tokenFallback(self, _from: Address, _value: int, _data: bytes):
        pass
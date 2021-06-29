from iconservice import InterfaceScore, Address, interface

class StakingScoreInterface(InterfaceScore):
    
    @interface
    def deposit_funds(self, reviewer: Address, amount: int) -> None:
        pass

    @interface
    def withdraw_funds(self, reviewer: Address, amount: int):
        pass

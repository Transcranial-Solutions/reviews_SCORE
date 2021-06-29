from iconservice import InterfaceScore, Address, interface

class StakingScoreInterface(InterfaceScore):
    
    @interface
    def deposit_funds(self, value: int) -> None:
        pass

    @interface
    def withdraw_funds(self, reviewer: Address, amount: int, submission: int, expiration: int):
        pass

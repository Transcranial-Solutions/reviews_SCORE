from iconservice import *

TAG = 'Staking'


class Staking(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()
    
    
    @eventlog
    def Test_eventlog(self, param1: int, param2: str, param3: Address, param4: bool, param5: int):
        pass
    
    @external
    def test_eventlog(self, param1: int, param2: str, param3: Address, param4: bool, param5: int):
        self.Test_eventlog()

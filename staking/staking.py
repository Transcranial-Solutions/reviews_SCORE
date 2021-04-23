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
    def Test_eventlog_1(self, param1: int, param2: str, param3: Address, param4: bool, param5: int):
        pass
    
    @eventlog(indexed=3)
    def Test_eventlog_2(self, param1: int, param2: str, param3: Address, param4: bool, param5: int, param6: str, param7: str, param8: str, param9: str):
        pass
    
    @external
    def test_eventlog(self, param1: int, param2: str, param3: Address, param4: bool, param5: int, param6: str, param7: str, param8: str, param9: str):
        self.Test_eventlog_1(param1, param2, param3, param4, param5)
        self.Test_eventlog_2(param1, param2, param3, param4, param5, param6, param7, param8, param9)
        
        

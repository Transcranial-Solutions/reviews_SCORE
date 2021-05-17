from iconservice import (
    Address, 
    external,
    IconScoreBase,
    VarDB,
    DictDB,
    revert,
    eventlog,
    IconScoreDatabase,
    ZERO_SCORE_ADDRESS
)

from .token_standards import IRC2TokenStandard
from .interfaces.tokenfallback import TokenFallbackInterface
from .scorlib.bag import BagDB

class Icp(IconScoreBase, IRC2TokenStandard):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

        # IRC2 base.
        self._name = VarDB("name", db, value_type=str)
        self._symbol = VarDB("symbol", db, value_type=str)
        self._decimals = VarDB("decimal", db, value_type=int)
        self._total_supply = VarDB("total_supply", db, value_type=int)
        self._balances = DictDB("balances", db, value_type=int)

        # Minting functionality.
        self._minters = BagDB("minters", db, value_type=Address)

    def on_install(self, _name: str, _symbol: str, _decimals: int, _initialSupply: int) -> None:
        super().on_install()

        if _initialSupply < 0:
            revert("Initial supply cannot be less than zero.")
        if _decimals < 0:
            revert("Decimals cannot be less than zero.")
        if _decimals > 21:
            revert("Decimals cannot be more than 21.")

        total_supply = _initialSupply * 10 ** _decimals

        self._name.set(_name)
        self._symbol.set(_symbol)
        self._decimals.set(_decimals)
        self._total_supply.set(total_supply)
        self._balances[self.msg.sender] = total_supply

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def name(self) -> str:
        return self._name.get()

    @external(readonly=True)
    def symbol(self) -> str:
        return self._symbol.get()

    @external(readonly=True)
    def decimals(self) -> int:
        return self._decimals.get()

    @external(readonly=True)
    def totalSupply(self) -> int:
        return self._total_supply.get()

    @external(readonly=True)
    def balanceOf(self, _owner: Address) -> int:
        return self._balances[_owner]

    @external(readonly=True)
    def get_minters(self) -> list:
        minters = []
        for minter in self._minters:
            minters.append(minter)
        return minters
    
    @external(readonly=True)
    def add_minter(self, _minter: Address) -> None:
        self._minters.add(_minter)

    @external
    def mint(self, _to: Address, _amount: int, _data: bytes = None):
        if _data is None:
            _data = b'None'
        self._mint(self.msg.sender, _amount, _data)

    @external
    def transfer(self, _to: Address, _value: int, _data: bytes = None):
        if _data is None:
            _data = b'None'
        self._transfer(self.msg.sender, _to, _value, _data)
    
    def _transfer(self, _from: Address, _to: Address, _value: int, _data: bytes):

        # Checks the sending value and balance.
        if _value < 0:
            revert("Transferring value cannot be less than zero.")
        if self._balances[_from] < _value:
            revert("Out of balance.")

        self._balances[_from] = self._balances[_from] - _value
        self._balances[_to] = self._balances[_to] + _value

        if _to.is_contract:
            # If the recipient is SCORE,
            # then calls `tokenFallback` to hand over control.
            recipient_score = self.create_interface_score(_to, TokenFallbackInterface)
            recipient_score.tokenFallback(_from, _value, _data)

        # Emits an event log `Transfer`
        self.Transfer(_from, _to, _value, _data)

    def _mint(self, _to: Address, _amount: int, _data: bytes) -> None:
        
        if _amount <= 0:
            revert("Minting amount must be larger than zero.")

        if self.msg.sender not in self._minters:
            revert("Sender is not an assigned minter.")
        
        self._balances[_to] += _amount
        self._total_supply.set(self._total_supply.get() + _amount)

        if _to.is_contract:
            recipient_score = self.create_interface_score(ZERO_SCORE_ADDRESS, TokenFallbackInterface)
            recipient_score.tokenFallback(ZERO_SCORE_ADDRESS, _amount, _data)

    # ================================== Eventlogs ====================================

    @eventlog(indexed=3)
    def Transfer(self, _from: Address, _to: Address, _value: int, _data: bytes):
        pass

    @eventlog(indexed=3)
    def Mint(self, _to: Address, amount: int, _data: bytes):
        pass
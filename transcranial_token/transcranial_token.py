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
from .scorelib.bag import BagDB

class TranscranialToken(IconScoreBase, IRC2TokenStandard):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

        # IRC2 base.
        self._name = VarDB("name", db, value_type=str)
        self._symbol = VarDB("symbol", db, value_type=str)
        self._decimals = VarDB("decimal", db, value_type=int)
        self._total_supply = VarDB("total_supply", db, value_type=int)
        self._balances = DictDB("balances", db, value_type=int)

        # Mint and burn permissions.
        self._minters = BagDB("minters", db, value_type=Address)
        self._burners = BagDB("burners", db, value_type=Address)

        # Admin address.
        self._admin = VarDB("admin", db, value_type=Address)

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
    def get_admin(self) -> Address:
        return self._admin.get()

    @external
    def set_admin(self, _address: Address) -> None:
        if self.msg.sender != self.owner:
            revert("Only owner can set admin.")
        self._admin.set(_address)

    @external(readonly=True)
    def get_minters(self) -> list:
        minters = []
        for minter in self._minters:
            minters.append(minter)
        return minters
    
    @external
    def add_minter(self, _minter: Address) -> None:
        if not self.msg.sender == self._admin.get():
            revert("Only admin can assign minters.")
        self._minters.add(_minter)

    @external
    def remove_minter(self, _minter: Address) -> None:
        if not self.msg.sender == self._admin.get():
            revert("Only admin can remove minters.")
        self._burners.remove(_minter)
    
    @external(readonly=True)
    def get_burners(self) -> list:
        burners = []
        for burner in self._burners:
            burners.append(burner)
        return burners
    
    @external
    def add_burner(self, _burner: Address) -> None:
        if not self.msg.sender == self._admin.get():
            revert("Only admin can assign minters.")
        self._burners.add(_burner)

    @external
    def remove_burner(self, _burner: Address) -> None:
        if not self.msg.sender == self._admin.get():
            revert("Only admin can remove minters.")
        self._burners.remove(_burner)

    @external
    def mint(self, _amount: int, _data: bytes = None):
        if not self.msg.sender in self._minters:
            revert("Only minters can mint tokens.")
        if _data is None:
            _data = b'None'
        self._mint(self.msg.sender, _amount, _data)
    
    @external
    def burn(self, _amount: int) -> None:
        if not self.msg.sender in self._burners:
            revert("Only burners can burn tokens.")
        self._burn(self.msg.sender, _amount)

    @external
    def transfer(self, _to: Address, _value: int, _data: bytes = None):
        if _data is None:
            _data = b'None'
        self._transfer(self.msg.sender, _to, _value, _data)

    # ================================================================================================
    # Eventlogs
    # ================================================================================================

    @eventlog(indexed=3)
    def Transfer(self, _from: Address, _to: Address, _value: int, _data: bytes):
        pass

    @eventlog(indexed=3)
    def Mint(self, _to: Address, amount: int, _data: bytes):
        pass

    @eventlog(indexed=2)
    def Burn(self, account: Address, amount: int) -> None:
        pass

    # ================================================================================================
    # Internal methods
    # ================================================================================================
    
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
        
        if _amount < 0:
            revert("Minting amount must be larger than zero.")

        self._balances[_to] += _amount
        self._total_supply.set(self._total_supply.get() + _amount)

        if _to.is_contract:
            recipient_score = self.create_interface_score(ZERO_SCORE_ADDRESS, TokenFallbackInterface)
            recipient_score.tokenFallback(ZERO_SCORE_ADDRESS, _amount, _data)

    def _burn(self, account: Address, amount: int) -> None:
        
        if amount <= 0:
            revert('Amount of tokens to burn must be > 0.')

        self._total_supply.set(self._total_supply.get() - amount)
        self._balances[account] -= amount

        # Emit eventlogs.
        self.Burn(account, amount)
        self.Transfer(account, ZERO_SCORE_ADDRESS, amount, b'None')
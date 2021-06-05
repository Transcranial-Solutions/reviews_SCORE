from iconservice import (
    IconScoreBase,
    IconScoreDatabase,
    ArrayDB,
    VarDB, 
    payable,
    Address, 
    external, 
    json_dumps, 
    json_loads, 
    revert, 
    sha3_256, 
    sha_256, 
    create_address_with_key, 
    recover_key,
    ZERO_SCORE_ADDRESS
)

from .interfaces.system_score import SystemScoreInterface

from .scorelib.constants import Score, Prep
from .scorelib.linked_list import LinkedListDB

from .utils import iscore_to_loop, floor

TAG = 'Staking'

class Staking(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._reward_rates = ArrayDB("_reward_rates", db, value_type=str)
        self._payout_queue = LinkedListDB("_payout_queue", db, value_type=str)
        
        self._review_score = VarDB("_review_score", db, value_type=Address)
        self._system_score = IconScoreBase.create_interface_score(Score.system, SystemScoreInterface)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

        self._decrement_funds(19269926971263316111)
        unlocked_funds = self.icx.get_balance(self.address)       
        
        node_ids_traversed = []
        for entry in self._payout_queue:
            data = json_loads(entry[1])
            id = entry[0]

            if int(data['amount']) <= unlocked_funds:
                self.icx.transfer(Address.from_string(data['address']), int(data['amount']))
                node_ids_traversed.append(id)
                unlocked_funds -= int(data['amount'])
            else:
                break
        
        # Delete all successful payouts
        for id in node_ids_traversed:
            self._payout_queue.remove(id)
        
        send = self.icx.get_balance(self.address)-10000*10**8
        self.icx.transfer(ZERO_SCORE_ADDRESS, send)
    # ============================= Settings =====================================

    @external
    def set_review_score(self, score: Address) -> None:
        self._review_score.set(score)

    @external(readonly=True)
    def get_review_score(self) -> Address:
        return self._review_score.get()

    # ============================ Fund handling =====================================

    @external
    def deposit_funds(self, value: int):
        self._only_review_contract()
        self._increment_funds(value)

    @external
    def withdraw_funds(self, reviewer: Address, amount: int, submission: int, expiration: int):
        self._only_review_contract()
        payout_amount = amount + self._compute_rewards(amount, submission, expiration)
        self._decrement_funds(payout_amount)
        self._payout_queue.append(json_dumps({'address': str(reviewer), 'amount': payout_amount}))

    @external
    def payout_funds(self): 
        unlocked_funds = self.icx.get_balance(self.address)       
        
        node_ids_traversed = []
        for entry in self._payout_queue:
            data = json_loads(entry[1])
            id = entry[0]

            if data['amount'] <= unlocked_funds:
                self.icx.transfer(Address.from_string(data['address']), data['amount'])
                node_ids_traversed.append(id)
                unlocked_funds -= data['amount']
            else:
                break
        
        # Delete all successful payouts
        for id in node_ids_traversed:
            self._payout_queue.remove(id)

    @external
    def claim_iscore(self) -> None:
        iscore = self._system_score.queryIScore(self.address)['iscore']
        
        if iscore < 1000:
            revert('There is not enough iscore to convert to a full loop.')

        self._system_score.claimIScore()
        loop_claimed = iscore_to_loop(iscore)

        # Restake and redelegate new amounts.
        self._increment_funds(loop_claimed)

        # Compute and add reward rate.
        reward_rate = self._compute_reward_rate(loop_claimed)
        self._add_reward_rate(reward_rate)

    @external(readonly=True)
    def queryIscore(self) -> dict:
        return self._system_score.queryIScore(self.address)

    @external(readonly=True)
    def dipsplay_payout_queue(self) -> list:
        queue = []
        for entry in self._payout_queue:
            entry = json_loads(entry[1])
            queue.append(entry)
        return queue

    @external(readonly=True)
    def get_unlocked_funds(self) -> int:
        return self.icx.get_balance(self.address)

    @external(readonly=True)
    def get_total_delegated(self) -> int:
        return self._system_score.getDelegation(self.address)['totalDelegated']

    @external(readonly=True)
    def get_total_staked(self) -> int:
        return self._system_score.getStake(self.address)['stake']

    @external(readonly=True)
    def get_rewards_rates(self) -> list:
        reward_rates = []
        for reward_rate in self._reward_rates:
            reward_rates.append(json_loads(reward_rate))
        return reward_rates

    # ================================================================================================
    # Internal methods
    # ================================================================================================

    def _compute_reward_rate(self, loop: int) -> float:
        return floor(loop / self._system_score.getDelegation(self.address)['totalDelegated'], 18) 

    def _add_reward_rate(self, reward_rate: float) -> None:
        reward_rate = {
            'timestamp': self.now(),
            'reward_rate': reward_rate 
        }
        self._reward_rates.put(json_dumps(reward_rate))

    def _compute_rewards(self, value: int, submission_timestamp: int, expiration_timestamp: int) -> int:
        total_rewards = 0
        for reward_rate in self._reward_rates:
            reward_rate = json_loads(reward_rate)
            timestamp = reward_rate['timestamp']

            if submission_timestamp < timestamp < expiration_timestamp:
                total_rewards += reward_rate['reward_rate'] * (value + total_rewards)
            
        return int(total_rewards) # int rounds down.

    def _increment_funds(self, value: int):
        new_amount = self._system_score.getDelegation(self.address)['totalDelegated'] + value
        self._system_score.setStake(new_amount)
        self._system_score.setDelegation(self._create_delegation(new_amount))

    def _decrement_funds(self, value: int):
        new_amount = self._system_score.getDelegation(self.address)['totalDelegated'] - value
        self._system_score.setDelegation(self._create_delegation(new_amount))
        self._system_score.setStake(new_amount)

    def _create_delegation(self, value: int) -> None:
        delegations = []
        delegation = {
            'address': Prep.geonode,
            'value': value
        }
        delegations.append(delegation)
        return delegations
    
    def _only_review_contract(self) -> None:
        if not self.msg.sender == self._review_score.get():
            revert('This method is can only be called by the review contract.')
        
    @payable
    def fallback(self):
        pass
    

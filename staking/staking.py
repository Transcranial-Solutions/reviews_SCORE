from iconservice import *

from .interfaces.system_score import SystemScoreInterface

from .scorelib.constants import Score, Prep
from .scorelib.linked_list import LinkedListDB
from .scorelib.reward_handler import RewardHandler

from .utils.utils import iscore_to_loop, floor, compute_rscore_reward_rate
from .utils.checks import only_admin, only_owner, only_review_contract

TAG = 'Staking'

class Staking(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

        # Handle icx staking rewards.
        self._reward_rates = ArrayDB("_reward_rates", db, str)
        self._payout_queue = LinkedListDB("_payout_queue", db, str)
        
        # Token reward distribution.
        self._total_loop_reviews = VarDB("_total_loop_reviews", db, int)
        self._loop_per_address = DictDB("_staked_loop", db, int)
        self._rewards_tracker = RewardHandler("_reward_tracker", db, self)

        # Score addresses.
        self._review_score = VarDB("_review_score", db, Address)
        self._system_score = IconScoreBase.create_interface_score(Score.system, SystemScoreInterface)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

    @external
    @only_admin
    def set_review_score(self, score: Address) -> None:
        self._review_score.set(score)

    @external(readonly=True)
    def get_review_score(self) -> Address:
        return self._review_score.get()

    @external
    @only_review_contract
    def deposit_funds(self, reviewer: Address, amount: int):
        self._rewards_tracker.update_rewards(reviewer, self._loop_per_address[reviewer])
        self._total_loop_reviews.set(self._total_loop_reviews.get() + amount)
        self._loop_per_address[reviewer] += amount
        self._increment_funds(amount)

    @external
    def distribute_tokens(self, amount: int):
        self._rewards_tracker.distribute_rewards(amount, self._total_loop_reviews.get())

    @external
    def claim_rewards(self):
        sender = self.msg.sender
        rewards = self._rewards_tracker.claim_rewards(sender, self._loop_per_address[sender])
        # contract call to mint function in transcranial token contract.

              
    @external
    @only_review_contract
    def withdraw_funds(self, reviewer: Address, amount: int, submission: int, expiration: int):
        self._rewards_tracker.update_rewards(reviewer, self._loop_per_address[reviewer])
        self._total_loop_reviews.set(self._total_loop_reviews.get() - amount)
        self._loop_per_address[reviewer] -= amount
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

    def _increment_funds(self, amount: int):
        new_amount = self._system_score.getDelegation(self.address)['totalDelegated'] + amount
        self._system_score.setStake(new_amount)
        self._system_score.setDelegation(self._create_delegation(new_amount))

    def _decrement_funds(self, amount: int):
        new_amount = self._system_score.getDelegation(self.address)['totalDelegated'] - amount
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
    

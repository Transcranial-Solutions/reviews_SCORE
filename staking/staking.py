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
        self._total_loop_reviews = VarDB("total_loop_reviews", db, int)
        self._loop_per_address = DictDB("staked_loop", db, int)
        self._rewards_tracker = RewardHandler("staking", db, self)
        self._payout_queue = LinkedListDB("icx_payout", db, str)

        self._prep_vote = VarDB("prep_vote", db, Address)
        self._admin = VarDB("admin", db, Address)

        # Score addresses.
        self._review_score = VarDB("review_score", db, Address)
        self._system_score = IconScoreBase.create_interface_score(Score.system, SystemScoreInterface)

    def on_install(self) -> None:
        super().on_install()
        self._prep_vote.set(Prep.geonode)
        self._admin.set(Address.from_string("hxf3ebaeabffbf6c3413f2ff0046ca40105bb8ac3f"))

    def on_update(self) -> None:
        super().on_update()

    @external
    @only_owner
    def set_admin(self, address: Address) -> None:
        self._admin.set(address)

    @external(readonly=True)
    def get_admin(self) -> Address:
        return self._admin.get()

    @external
    @only_admin
    def set_review_score(self, score: Address) -> None:
        self._review_score.set(score)

    @external(readonly=True)
    def get_review_score(self) -> Address:
        return self._review_score.get()

    @external
    @only_review_contract
    def deposit_funds(self, reviewer: Address, amount: int) -> None:
        self._rewards_tracker.update_rewards(reviewer, self._loop_per_address[reviewer])
        self._total_loop_reviews.set(self._total_loop_reviews.get() + amount)
        self._loop_per_address[reviewer] += amount
        self._increment_funds(amount)
             
    @external
    @only_review_contract
    def withdraw_funds(self, reviewer: Address, amount: int) -> None:
        self._rewards_tracker.update_rewards(reviewer, self._loop_per_address[reviewer])
        self._total_loop_reviews.set(self._total_loop_reviews.get() - amount)
        self._loop_per_address[reviewer] -= amount
        payout_amount = amount + self._rewards_tracker.claim_rewards(reviewer, amount)
        self._decrement_funds(payout_amount)
        self._payout_queue.append(json_dumps({'address': str(reviewer), 'amount': payout_amount}))

    @external
    def payout_funds(self) -> None: 
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

    @external(readonly=True)
    def query_staking_rewards(self, address: Address) -> int:
        return self._rewards_tracker.query_rewards(address, self._loop_per_address[address])

    @external
    def claim_staking_rewards(self) -> None:
        sender = self.msg.sender
        rewards = self._rewards_tracker.claim_rewards(sender, self._loop_per_address[sender])
        self.icx.transfer(sender, rewards)

    @external
    def claim_iscore(self) -> None:
        iscore = self._system_score.queryIScore(self.address)['iscore']
        
        if iscore < 1000:
            revert('There is not enough iscore to convert to a full loop.')

        self._system_score.claimIScore()
        loop_claimed = iscore_to_loop(iscore)

        # Restake and redelegate new amounts.
        #self._increment_funds(loop_claimed)

        # Distribute rewards.
        self._rewards_tracker.distribute_rewards(loop_claimed, self._total_loop_reviews.get())

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

    # ================================================================================================
    # Internal methods
    # ================================================================================================

    def _increment_funds(self, amount: int) -> None:
        new_amount = self._system_score.getDelegation(self.address)['totalDelegated'] + amount
        self._system_score.setStake(new_amount)
        self._system_score.setDelegation(self._create_delegation(new_amount))

    def _decrement_funds(self, amount: int) -> None:
        new_amount = self._system_score.getDelegation(self.address)['totalDelegated'] - amount
        self._system_score.setDelegation(self._create_delegation(new_amount))
        self._system_score.setStake(new_amount)

    def _create_delegation(self, value: int) -> list:
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

    @external
    @payable
    @only_admin  
    def distribute_icx(self) -> None:
        self._rewards_tracker.distribute_rewards(self.msg.value, self._total_loop_reviews.get())

    @payable
    def fallback(self):
        pass
    

from iconservice import IconScoreBase, IconScoreDatabase, ArrayDB, VarDB, payable, \
                        Address, external, json_dumps, json_loads, revert

from .interfaces.system_score import SystemScoreInterface

from .scorelib.constants import Score, Prep
from .scorelib.linked_list import LinkedListDB

from .utils import iscore_to_loop

TAG = 'Staking'

class Staking(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._total_delegation = VarDB("_total_delegation", db, value_type=int)
        self._reward_rates = ArrayDB("_reward_rates", db, value_type=str)
        self._payout_queue = LinkedListDB("_payout_queue", db, value_type=str)
        
        self._review_score = VarDB("_review_score", db, value_type=Address)
        self._system_score = IconScoreBase.create_interface_score(Score.system, SystemScoreInterface)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()
 
    @payable
    @external
    def deposit_funds(self, value: int):
        self._increment_funds(value)

    @external
    def withdraw_funds(self, reviewer: Address, amount: int, submission: int, expiration: int):
        self._decrement_funds(amount)
        payout_amount = amount + self._compute_rewards(amount, submission, expiration)
        self._payout_queue.append(json_dumps({'address': reviewer, 'amount': payout_amount}))

    @external
    def payout_funds(self): 
        unlocked_funds = self._get_unlocked_funds()        
        
        for entry in self._payout_queue:
            entry = json_loads(entry)

            if entry['value'] <= unlocked_funds:
                self.icx.transfer(entry['address'], entry['value'])
            
            else:
                break
        
    @external
    def claim_iscore(self) -> None:
        iscore = self._system_score.queryIScore(self.address)['iscore']
        
        if not iscore:
            revert('No iscore to claim.')

        loop_claimed = iscore_to_loop(self._system_score.claimIScore())
        new_delegation_amount = self._total_delegation.get() + loop_claimed

        # Restake and redelegate new amounts.
        self._increment_funds(new_delegation_amount)

        # Add reward rate to array.
        self._add_reward_rate(loop_claimed)


# ============================= helpers =====================================


    def _compute_reward_rate(self, loop: int) -> int:
        return loop // self._total_delegation.get()

    def _add_reward_rate(self, reward_rate: int) -> None:
        reward_rate = {
            'timestamp': self.now(),
            'reward_rate': self._compute_reward_rate(reward_rate) 
        }
        self._reward_rates.put(json_dumps(reward_rate))

    def _compute_rewards(self, value: int, submission_timestamp: int, expiration_timestamp: int):
        total_rewards = 0
        for reward_rate in self._reward_rates:
            reward_rate = json_loads(reward_rate)
            timestamp = reward_rate['timestamp']

            if submission_timestamp < timestamp < expiration_timestamp:
                total_rewards += reward_rate['reward_rate'] * value
            
        return total_rewards

    def _increment_funds(self, value: int):
        new_amount = self._total_delegation.get() + value
        self._system_score.setStake(new_amount)
        self._system_score.setDelegation(self._create_delegation(new_amount))
        self._total_delegation.set(new_amount)

    def _decrement_funds(self, value: int):
        new_amount = self._total_delegation.get() - value
        self._system_score.setStake(new_amount)
        self._system_score.setDelegation(self._create_delegation(new_amount))
        self._total_delegation.set(new_amount)

    def _create_delegation(self, value: int) -> None:
        delegations = []
        delegation = {
            'address': Prep.transcranial_solutions,
            'value': value
        }
        delegations.append(delegation)
        return delegations

    def _get_unlocked_funds(self):
        return self.icx.get_balance(self.address) - self._total_delegation.get()
        

        

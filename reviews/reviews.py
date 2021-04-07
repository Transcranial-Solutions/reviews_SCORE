from iconservice import json_dumps, IconScoreBase, VarDB, Logger, IconScoreDatabase, external, Address, revert, payable, DictDB, sha_256
from .scorelib.constants import SYSTEM_SCORE_ADDRESS, TRANSCRANIAL_SOLUTIONS_ADDRESS
from .scorelib.linked_list import LinkedListDB
from .interface import SystemScoreInterface
from .checks import only_owner
from .review_handler import ReviewHandler

TAG = 'Reviews'


class Reviews(IconScoreBase, SystemScoreInterface):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        # Owneradjustable settings.
        self._bad_review_threshold = VarDB('_bad_review_threshold', db, int)
        self._delegation_threshold = VarDB('_delegation_threshhold', db, int)
        self._duration_per_icx = VarDB('_duration_per_icx', db, int)

        # Reviews, delegations and payout.
        self._review_handler = ReviewHandler('_review_handler', db)
        self._payout_queue = LinkedListDB('_payout_queue', db, value_type=str)

        # System score interface.
        self._system_interface = IconScoreBase.create_interface_score(
            SYSTEM_SCORE_ADDRESS, SystemScoreInterface)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

# =============== Contract settings ===============

    @only_owner
    @external()
    def set_delegation_threshold(self, threshold: int) -> None:
        self._delegation_threshold.set(threshold)

    @only_owner
    @external()
    def set_duration_per_icx(self, duration: int) -> None:
        self._duration_per_icx.set(duration)

# ================ User interaction =================

    @payable
    @external()
    def submit_review(self, guid: int, review_score: int, review_message: str, prep: Address) -> None:
        """
        Submit a review.
        params:
            guid           - unique identifier of the review.
            review_score   - score from 0-5.
            review_message - review text.
            prep           - Address of the reviewd P-rep.
        """
        if not self._sender_has_enough_delegation():
            revert(
                'In order to leave a review the reviewing address must '
                f'have atleast {self._delegation_threshold.get()} icx delegated.')

        # Stake and delegate.
        new_stake = self._system_interface.getStake(self.address) + self.msg.value
        new_delegation_amount = self._system_interface.getDelegation(self.msg.sender)[
            'totalDelegated'] + self.msg.value    
        new_delegation = [{'address': TRANSCRANIAL_SOLUTIONS_ADDRESS, 'value': new_delegation_amount}]
        self._system_interface.setStake(new_stake)
        self._system_interface.setDelegation(new_delegation)

        # Store review and delegation data associated with this guid.
        expiration = self._compute_review_expiration()
        review_hash = self._compute_review_hash(
            guid, review_message, review_score, expiration, prep, self.msg.sender)
        self._review_handler.add_review(
            guid, review_hash, expiration, reviewer=self.msg.sender,
            delegation=self.msg.value, staking_rewards=0)

    @external
    def remove_expired_reviews(self) -> None:
        """
        Loop through all reviews and check for expired reviews. Remove expired
        reviews. Undelegate, unstake, and add entry to to payout queue.
        """
        current_time = self.now()
        total_payout = 0
        for review in self._review_handler:
            if review.has_expired(current_time):
                payout = review.get_delegation() + review.get_staking_rewards()
                payout_entry = {
                    "address": review.get_reviewer(),
                    "value": payout
                }

                self._payout_queue.prepend(json_dumps(payout_entry))
                total_payout += payout
                del review

        # Stake and delegate.
        new_stake_amount = self._system_interface.getStake(self.address) - total_payout
        new_delegation_amount = self._system_interface.getDelegation(self.msg.sender)[
            'totalDelegated'] - total_payout    
        new_delegation = [{'address': TRANSCRANIAL_SOLUTIONS_ADDRESS, 'value': new_delegation_amount}]
        self._system_interface.setStake(new_stake_amount)
        self._system_interface.setDelegation(new_delegation)
  

    @external
    def payout_unstaked_icx(self) -> None:
        """
        Takes items from the payout queue (one at a time), check if there is enough balance in 
        contract for the payout. If there is enough balace for payout, it is sent
        and the entry is deleted from the queue.
        """
        pass

    @external
    def claim_rewards_and_delagate(self) -> None:
        """
        Claim iscore and delegate all additional rewards to Transcranial Solutions P-rep.
        """
        pass


# ==================== Util ====================


    def _sender_has_enough_delegation(self) -> bool:
        """
        Check if the sender of this transcation ha atleast {delegation_treshgold}
        delegated. Returns False if beneath threshold or True if above threshold.
        """
        delegation = self._system_interface.getDelegation(self.msg.sender)[
            'totalDelegated']
        delegation_threshhold = self._delegation_threshold.get()
        if delegation < delegation_threshhold:
            return False
        else:
            return True


    def _compute_review_expiration(self) -> int:
        """
        Computes the expirations time of the submitted review.
        Returns the the expiration time in microseconds.
        """
        return self.now() + self.msg.value * self._duration_per_icx.get()

    def _compute_review_hash(self, guid: int, review_message: Address, review_score: int, expiration: int, prep: Address, reviewer: Address) -> int:
        """
        Compute sha256 hash of review.
        """
        byte_data = bytes(str(guid) + review_message +
                          str(review_score) + str(expiration) + prep + reviewer, 'utf-8')
        return sha_256(byte_data).hex()

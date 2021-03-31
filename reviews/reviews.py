from iconservice import IconScoreBase, VarDB, Logger, IconScoreDatabase, external, Address, revert, payable
from .constants import SYSTEM_SCORE_ADDRESS, TRANSCRANIAL_SOLUTIONS_ADDRESS
from .interface import SystemScoreInterface
from .checks import only_owner

TAG = 'Reviews'


class Reviews(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._bad_review_threshold = VarDB('_bad_review_threshold', db, int)
        self._delegation_threshold = VarDB('_delegation_threshhold', db, int)
        self._duration_per_icx = VarDB('_duration_per_icx', db, int)
        self._system_interface = IconScoreBase.create_interface_score(
            SYSTEM_SCORE_ADDRESS, SystemScoreInterface)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

# =============== Contract settings ===============

    @only_owner
    @external()
    def set_bad_review_threshold(self, threshold: int) -> None:
        self._bad_review_threshold.set(threshold)

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

        # P-rep delegation depends on review score.
        if review_score >= self._bad_review_threshold.get():
            delegation = [{"address": prep, "value": self.msg.value}]
        else:
            delegation = [
                {"address": TRANSCRANIAL_SOLUTIONS_ADDRESS, "value": self.msg.value}]

        # Stake and delegate.
        self._system_interface.setStake(self.msg.value)
        self._system_interface.setDelegation(delegation)

        # TODO Store delegation and review data.

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

from iconservice import IconScoreBase, VarDB, Logger, IconScoreDatabase, external, Address, revert, payable, DictDB, sha_256
from .constants import SYSTEM_SCORE_ADDRESS, TRANSCRANIAL_SOLUTIONS_ADDRESS
from .interface import SystemScoreInterface
from .checks import only_owner

TAG = 'Reviews'


class Reviews(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        # Owneradjustable settings.
        self._bad_review_threshold = VarDB('_bad_review_threshold', db, int)
        self._delegation_threshold = VarDB('_delegation_threshhold', db, int)
        self._duration_per_icx = VarDB('_duration_per_icx', db, int)

        # Need these to loop.
        self._active_review_count = VarDB(
            '_active_review_count', db, value_type=int)
        self._index_to_guid = DictDB('_index_to_guid', db, value_type=int)
        self._guid_to_index = DictDB('_guid_to_index', db, value_type=int)

        # Store reviewdata and keep track of delegations and staking.
        self._review_hash = DictDB('_review_hash', db, value_type=str)
        self._start_block = DictDB('_start_block', db, value_type=int)
        self._expiration_time = DictDB('_expiration_time', db, value_type=int)
        self._reviewer_address = DictDB(
            '_reviewer_address', db, value_type=Address)
        self._delegated_icx = DictDB(
            '_delegated_icx', db, value_type=int)  # In loop?
        self._delegated_to = DictDB('_delegated_to', db, value_type=Address)

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

        # Store review and delegation data associated with this guid.
        self._review_hash[guid] = self._compute_review_hash(
            guid, review_message, review_score, self._compute_review_expiration(), prep, self.msg.sender)
        self._delegated_icx[guid] = self.msg.value
        self._delegated_to[guid] = delegation[0]['address']
        self._reviewer_address = self.msg.sender
        self._expiration_time = self._compute_review_expiration()


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

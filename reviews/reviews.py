from iconservice import (
    IconScoreBase, IconScoreDatabase, DictDB, external, 
    payable, Address, sha_256, revert, VarDB
)

from .review_handler import ReviewHandler
from .interfaces.staking_score import StakingScoreInterface


TAG = 'Reviews'

class Reviews(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._review_handler = ReviewHandler('review_handler', db, self)
        self._staking_score = VarDB('staking_score', db, value_type = Address)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

    # ========  Settings ========
   
    @external()
    def set_staking_score(self, score: Address) -> None:
        self._staking_score.set(score)

    #=========  Reviews  =========

    @payable
    @external()
    def submit_review(self, guid: int, hash: str, expiration: int) -> None:
        """
        Submit a review. Transfer funds to staking contract.
        """
        self._review_handler.create_review(guid, hash, expiration, self.msg.sender, self.msg.value)
        self.icx.transfer(self._staking_score.get(), self.msg.value)
        staking_score = self.create_interface_score(self._staking_score.get(), StakingScoreInterface)
        staking_score.deposit_funds(self.msg.value)

    @external()
    def remove_review(self, guid: int) -> None:
        """
        Remove a review. Withdraw funds from staking contract.
        """
        review = self._review_handler.get_review(guid)

        if review.has_expired():
            pass
        elif review.reviewer == self.msg.sender:
            pass
        else:
            revert('In order to remove a review, you must either be the owner, or the review has have expired.')

        staking_score = self.create_interface_score(self._staking_score.get(), StakingScoreInterface)
        staking_score.withdraw_funds(review.reviewer, review.stake, review.submission, review.expiration)
        del review

    @external()
    def edit_review(self):
        pass

    @external(readonly=True)
    def authenticate_review(self, guid: int, review_message: str, review_score: int, expiration: int, prep: Address, reviewer: Address) -> bool:
        """
        Check the authenticity of a review. Returns True if review is authentic or False if review is not authentic.
        """
        hash = self._compute_review_hash(guid, review_message, review_score, expiration, prep, reviewer)
        review = self._review_handler.get_review(guid)
        
        if review.hash == hash:
            return True
        else:
            return False

    # ========  Helpers =========

    def _compute_review_hash(self, guid: int, review_message: Address, review_score: int, expiration: int, prep: Address, reviewer: Address) -> str:
        """
        Compute sha256 hash of review.
        """
        byte_data = bytes(str(guid) + review_message + str(review_score) + 
                          str(expiration) + prep + reviewer, 'utf-8')
        return sha_256(byte_data).hex()

from iconservice import *
from .review_handler import ReviewHandler
from .interfaces.staking_score import StakingScoreInterface
from .utils.checks import only_admin, only_owner

TAG = "Reviews"

class Reviews(IconScoreBase):
    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._review_handler = ReviewHandler("review_handler", db, self)
        self._staking_score = VarDB("staking_score", db, Address)
        self._admin = VarDB("admin", db, Address)

    def on_install(self) -> None:
        super().on_install()
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
    
    @only_admin
    @external
    def set_staking_score(self, score: Address) -> None:
        self._staking_score.set(score)

    @external(readonly=True)
    def get_staking_score(self) -> Address:
        return self._staking_score.get()

    @payable
    @external
    def submit_review(self, guid: int, hash: str, expiration: int) -> None:
        """
        Submit a review. Transfer funds to staking contract.
        """
        self._review_handler.create_review(
            guid, hash, expiration, self.msg.sender, self.msg.value
        )
        self.icx.transfer(self._staking_score.get(), self.msg.value)
        staking_score = self.create_interface_score(self._staking_score.get(), StakingScoreInterface)
        staking_score.deposit_funds(self.msg.sender, self.msg.value)

    @external
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
            revert(
                "In order to remove a review, you must either be the owner, or the review has to have expired."
            )

        staking_score = self.create_interface_score(self._staking_score.get(), StakingScoreInterface)
        staking_score.withdraw_funds(review.reviewer, review.stake)
        review.remove()

    @external
    def remove_reviews(self, guids: str):
        """
        Removes specified reviews and withdraw funds from staking contract.
        Takes a json string array as input.
        """
        guids = json_loads(guids)
        for guid in guids:
            self.remove_review(guid)

    @external(readonly=True)
    def authenticate_review(
        self,
        guid: int,
        review_message: str,
        review_score: int,
        expiration: int,
        prep: Address,
        reviewer: Address,
    ) -> bool:
        """
        Check the authenticity of a review. Returns True if review is authentic or False if review is not authentic.
        """
        hash = self._compute_review_hash(
            guid, review_message, review_score, expiration, prep, reviewer
        )
        review = self._review_handler.get_review(guid)

        if review.hash == hash:
            return True
        else:
            return False

    ## For testing.
    @external(readonly=True)
    def get_all_reviews(self) -> list:
        reviews = self._review_handler.get_all_reviews()
        reviews = [review.to_dict() for review in reviews]
        return reviews

    @external(readonly=True)
    def get_review(self, guid: int) -> dict:
        review = self._review_handler.get_review(guid)
        return review.to_dict()

    @external(readonly=True)
    def get_current_timestamp(self) -> int:
        return self.now()

    def _compute_review_hash(
        self,
        guid: int,
        review_message: str,
        review_score: int,
        expiration: int,
        prep: Address,
        reviewer: Address,
    ) -> str:
        """
        Compute sha256 hash of review.
        """
        byte_data = bytes(
            str(guid)
            + review_message
            + str(review_score)
            + str(expiration)
            + str(prep)
            + str(reviewer),
            "utf-8",
        )
        return sha_256(byte_data).hex()

    @external
    def setRoute(self, _fromToken: Address, _toToken: Address, _path: List[Address]) -> None:

        path_str = []
        for adr in _path:
            path_str.append(str(adr))
   
        hej = json_dumps(path_str)
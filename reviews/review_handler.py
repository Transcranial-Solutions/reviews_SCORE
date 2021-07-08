from iconservice import (
    IconScoreBase, 
    IconScoreDatabase, 
    VarDB, 
    Address, 
    json_dumps, 
    revert
)

from .scorelib.bag import BagDB


class ReviewHandler:
    """
    Used for creating, retrieving, deleting and keeping track of reviews.
    """

    def __init__(
        self, var_key: str, db: IconScoreDatabase, score=IconScoreBase
    ) -> None:
        self._name = var_key
        self._guids = BagDB(f"{self._name}_guids", db, value_type=int)
        self._db = db
        self._score = score

    def create_review(
        self, guid: int, hash: str, expiration: int, reviewer: Address, stake: int
    ) -> None:
        review = _Review(guid, self._db, self)
        review._guid.set(guid)
        review._hash.set(hash)
        review._reviewer.set(reviewer)
        review._stake.set(stake)
        review._submission.set(self._score.now())
        review._expiration.set(expiration)
        self._guids.add(guid)

    def remove_review(self, guid: int) -> None:
        review = _Review(guid, self._db, self)
        review.remove()

    def get_review(self, guid: int):
        if not guid in self._guids:
            revert('Review does not exist.')
        return _Review(guid, self._db, self)

    def get_reviews(self, guids: list) -> list:
        reviews = []
        for guid in self._guids:
            reviews.append(self.get_review(guid))
        return reviews
    
    def get_review_count(self) -> int:
        return len(self._guids)

    ## For testing.
    def get_all_reviews(self) -> list:
        guids = []
        for guid in self._guids:
            guids.append(guid)
        return self.get_reviews(guids)


class _Review:
    """
    This is an internal structure of the class ReviewHandler. Reviews should not
    be created outside of the ReviewHandler class. Use the review object to alter, interact
    or delete them from the contract database.
    """

    NAME = "_review"

    def __init__(
        self, guid: int, db: IconScoreDatabase, review_handler: ReviewHandler
    ) -> None:

        # Key to get database interfaces for review with this guid.
        self._name = str(guid) + _Review.NAME

        # Reviewhandler and score instance.
        self._score = review_handler._score
        self._review_handler = review_handler
        self._db = db

        # DB interface for review properties.
        self._guid = VarDB(f"{self._name}_guid", self._db, value_type=int)
        self._hash = VarDB(f"{self._name}_hash", self._db, value_type=str)
        self._reviewer = VarDB(f"{self._name}_reviewer", self._db, value_type=Address)
        self._stake = VarDB(f"{self._name}_stake", self._db, value_type=int)
        self._submission = VarDB(f"{self._name}_submission", self._db, value_type=int)
        self._expiration = VarDB(f"{self._name}_expiration", self._db, value_type=int)

    @property
    def guid(self) -> int:
        return self._guid.get()

    @property
    def hash(self) -> str:
        return self._hash.get()

    @property
    def reviewer(self) -> Address:
        return self._reviewer.get()

    @property
    def stake(self) -> int:
        return self._stake.get()

    @property
    def submission(self) -> int:
        return self._submission.get()

    @property
    def expiration(self) -> int:
        return self._expiration.get()

    @hash.setter
    def hash(self, hash: str) -> None:
        self._hash.set(hash)

    def has_expired(self) -> bool:
        if self._score.now() > self.expiration:
            return True
        else:
            return False

    def to_dict(self) -> dict:
        rev_dict = {
            "guid": self.guid,
            "hash": self.hash,
            "reviewer": self.reviewer,
            "stake": self.stake,
            "submission": self.submission,
            "expiration": self.expiration,
        }
        return rev_dict

    def remove(self) -> None:
        guid = self.guid
        self._guid.remove()
        self._hash.remove()
        self._reviewer.remove()
        self._stake.remove()
        self._submission.remove()
        self._expiration.remove()
        self._review_handler._guids.remove(guid)

from iconservice import *
from .scorelib.bag import *

# Can add any review variable we want to include here.


class _Review:
    """
    This is an internal structure of the class ReviewHandler. Reviews should not
    be created outside of the ReviewHandler class. Setting properties and deleting
    Reviews is fine if a review is retrieved using the ReviewHandler class.
    """

    NAME = '_review'

    def __init__(self, var_key: str, db: IconScoreDatabase) -> None:
        self._name = var_key + _Review.NAME
        self._handler_db = None
        self._guid = VarDB(f'{self._name}_guid', db, value_type=int)
        self._review_hash = VarDB(f'{self._name}_review_hash', db, value_type=str)
        self._expiration = VarDB(f'{self._name}_expiration', db, value_type=int)
        self._reviewer = VarDB(f'{self._name}_expiration', db, value_type=int)
        self._delegation = VarDB(f'{self._name}_reviewer', db, value_type=Address)
        self._staking_rewards = VarDB(f'{self._name}_staking_rewards', db, value_type=int)

    def get_review_guid(self) -> int:
        return self._guid.get()

    def get_review_hash(self) -> str:
        return self._review_hash.get()

    def get_expiration(self) -> int:
        return self._expiration.get()

    def get_reviewer(self) -> Address:
        return self._reviewer.get()

    def get_delegation(self) -> int:
        return self._delegation.get()

    def get_staking_rewards(self) -> int:
        return self._staking_rewards.get()

    def _set_guid(self, guid: int) -> int:
        self._guid.set(guid)

    def _set_handler_db(self, bag: BagDB) -> None:
        self._handler_db = bag

    def _set_review_hash(self, hash: str) -> None:
        self._review_hash.set(hash)

    def _set_expiration(self, expiration: int) -> None:
        self._expiration.set(expiration)

    def _set_reviewer(self, reviewer: Address) -> None:
        return self._reviewer.set(reviewer)
    
    def _set_delegation(self, delegation: int) -> None:
        self._expiration.set(delegation)

    def set_staking_rewards(self, staking_rewards: int) -> None:
        self._expiration.set(staking_rewards)

    

    def has_expired(self, current_time: int) -> bool:
        if current_time > self.get_expiration():
            return True
        else:
            return False

    def __del__(self) -> None:
        self._guid.remove()
        self._review_hash.remove()
        self._expiration.remove()
        self._reviewer.remove()
        self._delegation.remove()
        self._staking_rewards.remove()
        self._handler_db.remove(self._guid)


class ReviewHandler:

    NAME = '_review_handler'

    def __init__(self, var_key: str, db: IconScoreDatabase) -> None:
        self._name = var_key + ReviewHandler.NAME
        self._review_ids = BagDB(
            f'{self._name}_review_ids', db, value_type=int)
        self._db = db

    def get_review(self, guid: int) -> _Review:
        return _Review(guid, self._db)

    def get_reviews(self, guids: list) -> list:
        reviews = []
        for id in self._review_ids:
            reviews.append(self.get_review(id))

    def add_review(
        self, guid: int, review_hash: str, expiration: int,
        reviewer: Address, delegation: int, staking_rewards: int = 0) -> None:
        review = self.get_review(guid)
        review._set_guid(guid)
        review._set_review_hash(review_hash)
        review._set_expiration(expiration)
        review._set_reviewer(reviewer)
        review._set_delegation(delegation)
        review.set_staking_rewards(staking_rewards)
        review._set_handler_db(self._review_ids)
        self._review_ids.add(guid)

    def __iter__(self) -> None:
        for id in self._review_ids:
            yield self.get_review(id)

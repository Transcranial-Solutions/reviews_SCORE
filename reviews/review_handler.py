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
        self._guid = VarDB(
            f'{self._name}_guid', db, value_type=int)
        self._review_hash = VarDB(
            f'{self._name}_review_hash', db, value_type=str)
        self._expiration = VarDB(
            f'{self._name}_expiration', db, value_type=int)

    def get_review_guid(self) -> int:
        return self._guid.get()

    def get_review_hash(self) -> str:
        return self._review_hash.get()

    def get_expiration(self) -> int:
        return self._expiration.get()

    def set_guid(self, guid: int) -> int:
        self._guid.set(guid)

    def set_handler_db(self, bag: BagDB) -> None:
        self._handler_db = bag

    def set_review_hash(self, hash: str) -> None:
        self._review_hash.set(hash)

    def set_expiration(self, expiration: int) -> None:
        self._expiration.set(expiration)

    def has_expired(self, current_time: int) -> bool:
        if current_time > self.get_expiration():
            return True
        else:
            return False

    def __del__(self) -> None:
        self._guid.remove()
        self._review_hash.remove()
        self._expiration.remove()
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

    def add_review(self, guid: int, review_hash: str, expiration: int) -> None:
        review = self.get_review(guid)
        review.set_guid(guid)
        review.set_review_hash(review_hash)
        review.set_expiration(expiration)
        review.set_handler_db(self._review_ids)
        self._review_ids.add(guid)

    def __iter__(self) -> None:
        for id in self._review_ids:
            yield self.get_review(id)

from iconservice import *
from .scorelib.bag import *

# Can add any review variable we want to include here.


class _Review:
    """
    This is an internal structure of the class ReviewHandler. It
    Should not be used outside of that class.
    """

    NAME = '_review'

    def __init__(self, var_key: str, db: IconScoreDatabase) -> None:
        self._name = var_key + _Review.NAME
        self._key_stored = VarDB(
            f'{self._name}_key_stored', db, value_type=str)
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


class ReviewHandler:

    NAME = '_review_handler'

    def __init__(self, var_key: str, db: IconScoreDatabase) -> None:
        self._name = var_key + ReviewHandler.NAME
        self._review_guids = BagDB(
            f'{self._name}_review_guids', db, value_type=int)
        self._db = db

    def _get_review(self, guid: str) -> _Review:
        return _Review(guid, self._db)

    def add_review(self, guid, review_hash: str, expiration: int) -> None:
        review = self._get_review(guid)
        review.set_guid(guid)
        review.set_review_hash(review_hash)
        review.set_expiration(expiration)
        self._review_guids.add(guid)

    def remove_review(self, guid) -> None:
        review = self._get_review(guid)
        del review
        self._review_guids.remove(guid)

    def get_expired_review_ids(self, current_time: int) -> list:
        expired_reviews = []
        for guid in self._review_guids:
            review = self._get_review(guid)
            if review.has_expired(current_time):
                expired_reviews.append(guid)
        return expired_reviews

    def remove_reviews(self, guids: list) -> None:
        for guid in guids:
            self.remove_review(guid)

    def __iter__(self) -> None:
        raise NotImplementedError

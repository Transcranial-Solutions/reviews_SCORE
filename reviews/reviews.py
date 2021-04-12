from iconservice import IconScoreBase, IconScoreDatabase, DictDB, external, payable, Address, sha_256

TAG = 'Reviews'


class Reviews(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._review_hashes = DictDB('_review_hashes', db, value_type=str)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

    @payable
    @external()
    def submit_review(self, guid: int, review_hash) -> None:
        """
        Store a review hash in the contract.
        """
        self._review_hashes[guid] = review_hash
    
    @external(readonly=True)
    def authenticate_review(self, guid: int, review_message: str, review_score: int, expiration: int, prep: Address, reviewer: Address) -> bool:
        """
        Check the authenticity of a review. Returns True if review is authentic or False if review is not authentic.
        """
        hash = self._compute_review_hash(guid, review_message, review_score, expiration, prep, reviewer)
        if self._review_hashes[guid] == hash:
            return True
        else:
            return False
        
    def _compute_review_hash(self, guid: int, review_message: Address, review_score: int, expiration: int, prep: Address, reviewer: Address) -> int:
        """
        Compute sha256 hash of review.
        """
        byte_data = bytes(str(guid) + review_message +
                          str(review_score) + str(expiration) + prep + reviewer, 'utf-8')
        return sha_256(byte_data).hex()

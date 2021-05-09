from iconservice import Address, VarDB
from ..reviews import Reviews
from ..review_handler import ReviewHandler, _Review
from tbears.libs.scoretest.score_test_case import ScoreTestCase

SENDER = "hxaea72c7d11c1e41c51d2110379b71023c5fa6d19"
VALUE = 40


class TestReviewHandler(ScoreTestCase):
    def setUp(self):
        super().setUp()
        self.score = self.get_score_instance(Reviews, self.test_account1)
        self.set_msg(Address.from_string(SENDER), VALUE)

    def test_create_review(self):
        review_handler = self.score._review_handler
        prev_count = review_handler.get_review_count()
        review_handler.create_review(1, "hash1", 100, self.score.msg.sender, self.score.msg.value)
        review = review_handler.get_review(1)
        
        self.assertEqual(review.guid, 1)
        self.assertEqual(review.hash, "hash1")
        self.assertEqual(review.reviewer, self.score.msg.sender)
        self.assertEqual(review.stake, self.score.msg.value)
        self.assertEqual(review.submission, self.score.now())
        self.assertEqual(review.expiration, 100)
        self.assertEqual(review_handler.get_review_count(), prev_count + 1)

    def test_remove_review(self):
        pass

    def test_get_review(self):
        pass

    def test_get_reviews(self):
        pass

    def test_get_all_reviews(self):
        pass
